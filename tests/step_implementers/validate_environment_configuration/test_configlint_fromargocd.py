# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
import os

from testfixtures import TempDirectory
from tssc.step_implementers.validate_environment_configuration import ConfiglintFromArgocd
from tssc.step_result import StepResult

from tests.helpers.base_step_implementer_test_case import BaseStepImplementerTestCase


class TestStepImplementerConfiglintFromArgocd(BaseStepImplementerTestCase):
    def create_step_implementer(
            self,
            step_config={},
            step_name='',
            implementer='',
            results_dir_path='',
            results_file_name='',
            work_dir_path=''
    ):
        return self.create_given_step_implementer(
            step_implementer=ConfiglintFromArgocd,
            step_config=step_config,
            step_name=step_name,
            implementer=implementer,
            results_dir_path=results_dir_path,
            results_file_name=results_file_name,
            work_dir_path=work_dir_path
        )

    # TESTS FOR configuration checks
    def test_step_implementer_config_defaults(self):
        defaults = ConfiglintFromArgocd.step_implementer_config_defaults()
        expected_defaults = {
        }
        self.assertEqual(expected_defaults, defaults)

    def test_required_runtime_step_config_keys(self):
        required_keys = ConfiglintFromArgocd.required_runtime_step_config_keys()
        expected_required_keys = []
        self.assertEqual(required_keys, expected_required_keys)

    def test_run_step_pass(self):
        with TempDirectory() as temp_dir:
            results_dir_path = os.path.join(temp_dir.path, 'tssc-results')
            results_file_name = 'tssc-results.yml'
            work_dir_path = os.path.join(temp_dir.path, 'working')
            test_file_name = 'yamlnotused'
            test_file_path = os.path.join(temp_dir.path, test_file_name)
            temp_dir.write(test_file_path, b'ignored')

            step_config = {}
            artifact_config = {
                'path': {
                    'value': f'file://{test_file_path}'
                }
            }
            self.setup_previous_result(work_dir_path, artifact_config)

            step_implementer = self.create_step_implementer(
                step_config=step_config,
                step_name='validate-environment-configuration',
                implementer='ConfiglintArgocd',
                results_dir_path=results_dir_path,
                results_file_name=results_file_name,
                work_dir_path=work_dir_path,
            )

            result = step_implementer._run_step()

            expected_step_result = StepResult(
                step_name='validate-environment-configuration',
                sub_step_name='ConfiglintArgocd',
                sub_step_implementer_name='ConfiglintArgocd'
            )

            # expected_step_result.add_artifact(name='yml-path', value=f'file://{test_file_path}')
            expected_step_result.add_artifact(name='yml-path', value=f'{test_file_path}')
            self.assertEqual(expected_step_result.get_step_result(), result.get_step_result())

    def test_run_step_fail_missing_path_from_deploy(self):
        with TempDirectory() as temp_dir:
            results_dir_path = os.path.join(temp_dir.path, 'tssc-results')
            results_file_name = 'tssc-results.yml'
            work_dir_path = os.path.join(temp_dir.path, 'working')

            step_config = {}
            artifact_config = {
            }
            self.setup_previous_result(work_dir_path, artifact_config)

            step_implementer = self.create_step_implementer(
                step_config=step_config,
                step_name='validate-environment-configuration',
                implementer='ConfiglintArgocd',
                results_dir_path=results_dir_path,
                results_file_name=results_file_name,
                work_dir_path=work_dir_path,
            )

            result = step_implementer._run_step()

            expected_step_result = StepResult(
                step_name='validate-environment-configuration',
                sub_step_name='ConfiglintArgocd',
                sub_step_implementer_name='ConfiglintArgocd'
            )
            expected_step_result.success = False
            expected_step_result.message = 'Step results missing path from deploy step'
            self.assertEqual(expected_step_result.get_step_result(), result.get_step_result())

    def test_run_step_fail_missing_path_file_from_deploy(self):
        with TempDirectory() as temp_dir:
            results_dir_path = os.path.join(temp_dir.path, 'tssc-results')
            results_file_name = 'tssc-results.yml'
            work_dir_path = os.path.join(temp_dir.path, 'working')
            test_file_name = 'yamlnotused'
            test_file_path = os.path.join(temp_dir.path, test_file_name)
            temp_dir.write(test_file_path, b'ignored')

            step_config = {}
            artifact_config = {
                'path': {
                    'value': f'file://{test_file_path}.bad'
                }
            }
            self.setup_previous_result(work_dir_path, artifact_config)

            step_implementer = self.create_step_implementer(
                step_config=step_config,
                step_name='validate-environment-configuration',
                implementer='ConfiglintArgocd',
                results_dir_path=results_dir_path,
                results_file_name=results_file_name,
                work_dir_path=work_dir_path,
            )

            result = step_implementer._run_step()

            expected_step_result = StepResult(
                step_name='validate-environment-configuration',
                sub_step_name='ConfiglintArgocd',
                sub_step_implementer_name='ConfiglintArgocd'
            )
            expected_step_result.success = False
            expected_step_result.message = f'File not found {test_file_path}.bad'
            self.assertEqual(expected_step_result.get_step_result(), result.get_step_result())

