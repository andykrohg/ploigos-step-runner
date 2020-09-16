"""Step Implementer for the unit-test step for Maven generating JUnit reports.

Step Configuration
------------------

Step configuration expected as input to this step.
Could come from either configuration file or
from runtime configuration.

| Configuration Key  | Required? | Default     | Description
|--------------------|-----------|-------------|-----------
| `fail-on-no-tests` | True      | True        | Value to specify whether unit-test
                                                 step can succeed when no tests are defined
| `pom-file`         | True      | `'pom.xml'` | pom used to run tests and check
                                                 for existence of custom reportsDirectory

Expected Previous Step Results
------------------------------

Results expected from previous steps that this step requires.

None.

Results
-------

Results output by this step.

| Result Key         | Description
|--------------------|------------
| `result`           | A dictionary describing the unit test step results
| `options`          | A dictionary of non-standard options used by this step implementer
| `report-artifacts` | An array of dictionaries describing artifacts \
                       generated by this step implementer

**result**
Keys in the `result` dictionary element in the `unit-test` dictionary of the step results.

| `result` Key | Description
|--------------|------------
| `success`    | Boolean value describing success/failure of this step
| `message`    | Human readable message describing results of this step

**options**
Keys in the `options` dictionary element in the `unit-test` dictionary of the step results.
These keys are to be minimally displayed only when a non-default value is used.

| `options` Key       | Description
|---------------------|------------
| `pom-path`          | Absolute path to the pom used to run tests
| `fail-on-no-tests`  | Boolean value describing whether or not step should fail \
                        when unit tests are missing

**report-artifacts**
Keys in the `report-artifacts` array in the `unit-test` dictionary of the step results.
Elements in this array are minimally shown when reports are generated. When no reports are \
generated, this array remains empty.

| `report-artifacts` Key | Description
|------------------------|------------
| `name`                 | Human readable name for report artifact generated by this step
| `path`                 | Absolute path (including transport protocol) to the step report artifact
"""
import sys
import os
import sh

from tssc import StepImplementer
from tssc.utils.xml import get_xml_element_by_path

DEFAULT_CONFIG = {
    'fail-on-no-tests': True,
    'pom-file': 'pom.xml'
}

REQUIRED_CONFIG_KEYS = [
    'fail-on-no-tests',
    'pom-file'
]

class Maven(StepImplementer):
    """
    StepImplementer for the unit-test step for Maven generating JUnit reports.
    """

    @staticmethod
    def step_implementer_config_defaults():
        """
        Getter for the StepImplementer's configuration defaults.

        Notes
        -----
        These are the lowest precedence configuration values.

        Returns
        -------
        dict
            Default values to use for step configuration values.
        """
        return DEFAULT_CONFIG

    @staticmethod
    def required_runtime_step_config_keys():
        """
        Getter for step configuration keys that are required before running the step.

        See Also
        --------
        _validate_runtime_step_config

        Returns
        -------
        array_list
            Array of configuration keys that are required before running the step.
        """
        return REQUIRED_CONFIG_KEYS

    def _run_step(self):
        """Runs the TSSC step implemented by this StepImplementer.

        Returns
        -------
        dict
            Results of running this step.
        """
        pom_file = self.get_config_value('pom-file')
        fail_on_no_tests = self.get_config_value('fail-on-no-tests')

        if not os.path.exists(pom_file):
            raise ValueError('Given pom file does not exist: ' + pom_file)

        surefire_path = 'mvn:build/mvn:plugins/mvn:plugin/[mvn:artifactId="maven-surefire-plugin"]'
        maven_surefire_plugin = get_xml_element_by_path(
            pom_file,
            surefire_path,
            default_namespace='mvn'
        )
        if maven_surefire_plugin is None:
            raise ValueError('Unit test dependency "maven-surefire-plugin" missing from POM.')

        reports_dir = get_xml_element_by_path(
            pom_file,
            f'{surefire_path}/mvn:configuration/mvn:reportsDirectory',
            default_namespace='mvn'
        )
        if reports_dir is not None:
            test_results_dir = reports_dir.text
        else:
            test_results_dir = os.path.join(
                os.path.dirname(os.path.abspath(pom_file)),
                'target/surefire-reports')

        try:
            sh.mvn(  # pylint: disable=no-member
                'clean',
                'test',
                '-f', pom_file,
                _out=sys.stdout,
                _err=sys.stderr
            )
        except sh.ErrorReturnCode as error:
            raise RuntimeError("Error invoking mvn: {error}".format(error=error)) from error

        test_results_output_path = test_results_dir

        if not os.path.isdir(test_results_dir) or \
            len(os.listdir(test_results_dir)) == 0:
            if fail_on_no_tests is not True:
                results = {
                    'result': {
                        'success': True,
                        'message': 'unit test step run successfully, but no tests were found'
                    },
                    'report-artifacts': [],
                    'options': {
                        'pom-path': pom_file,
                        'fail-on-no-tests': False
                    }
                }
            else:# pragma: no cover
                # Added 'no cover' to bypass missing unit-test step coverage error
                # that is covered by the following unit test:
                #   test_unit_test_run_attempt_fails_fail_on_no_tests_flag_true
                raise RuntimeError('Error: No unit tests defined')
        else:
            results = {
                'result': {
                    'success': True,
                    'message': 'unit test step run successfully and junit reports were generated'
                },
                'options': {
                    'pom-path': pom_file
                },
                'report-artifacts': [
                    {
                        'name': 'maven unit test results generated using junit',
                        'path': f'file://{test_results_output_path}'
                    }
                ]
            }
        return results
