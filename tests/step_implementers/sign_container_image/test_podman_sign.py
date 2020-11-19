# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
import re

from tssc.step_implementers.sign_container_image import PodmanSign
from tests.helpers.base_step_implementer_test_case import BaseStepImplementerTestCase


class TestStepImplementerPodmanSignSourceBase(BaseStepImplementerTestCase):
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
            step_implementer=PodmanSign,
            step_config=step_config,
            step_name=step_name,
            implementer=implementer,
            results_dir_path=results_dir_path,
            results_file_name=results_file_name,
            work_dir_path=work_dir_path
        )

# TESTS FOR configuration checks
    def test_step_implementer_config_defaults(self):
        defaults = PodmanSign.step_implementer_config_defaults()
        expected_defaults = {}
        self.assertEqual(defaults, expected_defaults)

    def test_required_runtime_step_config_keys(self):
        required_keys = PodmanSign.required_runtime_step_config_keys()
        expected_required_keys = ['container-image-signer-pgp-private-key']
        self.assertEqual(required_keys, expected_required_keys)

    def test__validate_runtime_step_config_valid(self):
        step_config = {
            'container-image-signer-pgp-private-key':'test'
        }
        step_implementer = self.create_step_implementer(
            step_config=step_config,
            step_name='sign-container-image',
            implementer='PodmanSign'
        )

        step_implementer._validate_runtime_step_config(step_config)

    def test__validate_runtime_step_config_invalid(self):
        step_config = {
        }
        step_implementer = self.create_step_implementer(
            step_config=step_config,
            step_name='sign-container-image',
            implementer='PodmanSign'
        )
        with self.assertRaisesRegex(
                AssertionError,
                "The runtime step configuration \({}\) is missing "
                "the required configuration keys "
                "\(\['container-image-signer-pgp-private-key'\]\)"
        ):
            step_implementer._validate_runtime_step_config(step_config)
