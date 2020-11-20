# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
import os
from unittest.mock import patch
import sh

from testfixtures import TempDirectory
from tests.helpers.base_step_implementer_test_case import BaseStepImplementerTestCase
from tssc.step_implementers.sign_container_image import CurlPush
from tssc.step_result import StepResult


class TestStepImplementerCurlPushSourceBase(BaseStepImplementerTestCase):
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
            step_implementer=CurlPush,
            step_config=step_config,
            step_name=step_name,
            implementer=implementer,
            results_dir_path=results_dir_path,
            results_file_name=results_file_name,
            work_dir_path=work_dir_path
        )

    # TESTS FOR configuration checks
    def test_step_implementer_config_defaults(self):
        defaults = CurlPush.step_implementer_config_defaults()
        expected_defaults = {}
        self.assertEqual(defaults, expected_defaults)

    def test_required_runtime_step_config_keys(self):
        required_keys = CurlPush.required_runtime_step_config_keys()
        expected_required_keys = [
            'container-image-signature-server-url',
            'container-image-signature-server-username',
            'container-image-signature-server-password'
        ]
        self.assertEqual(required_keys, expected_required_keys)

    def test__validate_runtime_step_config_valid(self):
        step_config = {
            'container-image-signature-server-url': 'test',
            'container-image-signature-server-username': 'test',
            'container-image-signature-server-password': 'test'
        }
        step_implementer = self.create_step_implementer(
            step_config=step_config,
            step_name='sign-container-image',
            implementer='CurlPush'
        )

        step_implementer._validate_runtime_step_config(step_config)

    def test__validate_runtime_step_config_invalid(self):
        step_config = {
        }
        step_implementer = self.create_step_implementer(
            step_config=step_config,
            step_name='sign-container-image',
            implementer='CurlPush'
        )
        with self.assertRaisesRegex(
                AssertionError,
                r"The runtime step configuration \({}\) is missing "
                r"the required configuration keys "
                r"\(\['container-image-signature-server-url', "
                r"'container-image-signature-server-username', "
                r"'container-image-signature-server-password'\]\)"
        ):
            step_implementer._validate_runtime_step_config(step_config)

    @patch('sh.curl', create=True)
    def test_run_step_pass(self, curl_mock):
        with TempDirectory() as temp_dir:
            results_dir_path = os.path.join(temp_dir.path, 'tssc-results')
            results_file_name = 'tssc-results.yml'
            work_dir_path = os.path.join(temp_dir.path, 'working')
            signature_file_path = 'signature-1'
            temp_dir.write(signature_file_path, b'bogus signature')
            container_image_signature_file_path = os.path.join(temp_dir.path, signature_file_path)

            step_config = {
                'container-image-signature-server-url': 'https://sigserver/signatures',
                'container-image-signature-server-username': 'admin',
                'container-image-signature-server-password': 'adminPassword'
            }

            # Previous (fake) results
            artifact_config = {
                'container-image-signature-file-path': {'value': container_image_signature_file_path},
                'container-image-signature-name': {'value': 'myname'},
            }
            self.setup_previous_result(work_dir_path, artifact_config)

            # Actual results
            step_implementer = self.create_step_implementer(
                step_config=step_config,
                step_name='sign-container-image',
                implementer='CurlPush',
                results_dir_path=results_dir_path,
                results_file_name=results_file_name,
                work_dir_path=work_dir_path,
            )
            result = step_implementer._run_step()

            # # Expected results
            expected_step_result = StepResult(step_name='sign-container-image', sub_step_name='CurlPush',
                                              sub_step_implementer_name='CurlPush')
            expected_step_result.add_artifact(name='container-image-signature-file-md5',
                                              value='b66c5c3d4ab37a50e69a05d72ba302fa')
            expected_step_result.add_artifact(name='container-image-signature-file-sha1',
                                              value='d9ba1fc747829392883c48adfe4bb688239dc8b2')
            expected_step_result.add_artifact(name='container-image-signature-url',
                                              value='https://sigserver/signatures/myname')
            self.assertEqual(expected_step_result.get_step_result(), result.get_step_result())

    @patch('sh.curl', create=True)
    def test_run_step_fail(self, curl_mock):
        with TempDirectory() as temp_dir:
            results_dir_path = os.path.join(temp_dir.path, 'tssc-results')
            results_file_name = 'tssc-results.yml'
            work_dir_path = os.path.join(temp_dir.path, 'working')
            signature_file_path = 'signature-1'
            temp_dir.write(signature_file_path, b'bogus signature')
            container_image_signature_file_path = os.path.join(temp_dir.path, signature_file_path)

            step_config = {
                'container-image-signature-server-url': 'https://sigserver/signatures',
                'container-image-signature-server-username': 'admin',
                'container-image-signature-server-password': 'adminPassword'
            }

            # Previous (fake) results
            artifact_config = {
                'container-image-signature-file-path': {'value': container_image_signature_file_path},
                'container-image-signature-name': {'value': 'myname'},
            }
            self.setup_previous_result(work_dir_path, artifact_config)

            # Actual results
            step_implementer = self.create_step_implementer(
                step_config=step_config,
                step_name='sign-container-image',
                implementer='CurlPush',
                results_dir_path=results_dir_path,
                results_file_name=results_file_name,
                work_dir_path=work_dir_path,
            )
            sh.curl.side_effect = sh.ErrorReturnCode('curl', b'mock stdout', b'mock error')
            with self.assertRaisesRegex(
                    RuntimeError,
                    'Unexpected error curling signature file to signature server: .*'):
                step_implementer._run_step()

    @patch('sh.curl', create=True)
    def test_run_step_fail_missing_previous_step_file_path(self, curl_mock):
        with TempDirectory() as temp_dir:
            results_dir_path = os.path.join(temp_dir.path, 'tssc-results')
            results_file_name = 'tssc-results.yml'
            work_dir_path = os.path.join(temp_dir.path, 'working')
            signature_file_path = 'signature-1'
            temp_dir.write(signature_file_path, b'bogus signature')
            container_image_signature_file_path = os.path.join(temp_dir.path, signature_file_path)

            step_config = {
                'container-image-signature-server-url': 'https://sigserver/signatures',
                'container-image-signature-server-username': 'admin',
                'container-image-signature-server-password': 'adminPassword'
            }

            # Previous (fake) results
            artifact_config = {
                # 'container-image-signature-file-path': {'value': container_image_signature_file_path},
                'container-image-signature-name': {'value': 'myname'},
            }
            self.setup_previous_result(work_dir_path, artifact_config)

            # Actual results
            step_implementer = self.create_step_implementer(
                step_config=step_config,
                step_name='sign-container-image',
                implementer='CurlPush',
                results_dir_path=results_dir_path,
                results_file_name=results_file_name,
                work_dir_path=work_dir_path,
            )
            result = step_implementer._run_step()

            # # Expected results
            expected_step_result = StepResult(step_name='sign-container-image', sub_step_name='CurlPush',
                                              sub_step_implementer_name='CurlPush')
            expected_step_result.success = False
            expected_step_result.message = "Missing container-image-signature-file-path"
            self.assertEqual(expected_step_result.get_step_result(), result.get_step_result())

    @patch('sh.curl', create=True)
    def test_run_step_fail_missing_previous_step_name(self, curl_mock):
        with TempDirectory() as temp_dir:
            results_dir_path = os.path.join(temp_dir.path, 'tssc-results')
            results_file_name = 'tssc-results.yml'
            work_dir_path = os.path.join(temp_dir.path, 'working')
            signature_file_path = 'signature-1'
            temp_dir.write(signature_file_path, b'bogus signature')
            container_image_signature_file_path = os.path.join(temp_dir.path, signature_file_path)

            step_config = {
                'container-image-signature-server-url': 'https://sigserver/signatures',
                'container-image-signature-server-username': 'admin',
                'container-image-signature-server-password': 'adminPassword'
            }

            # Previous (fake) results
            artifact_config = {
                'container-image-signature-file-path': {'value': container_image_signature_file_path},
                # 'container-image-signature-name': {'value': 'myname'},
            }
            self.setup_previous_result(work_dir_path, artifact_config)

            # Actual results
            step_implementer = self.create_step_implementer(
                step_config=step_config,
                step_name='sign-container-image',
                implementer='CurlPush',
                results_dir_path=results_dir_path,
                results_file_name=results_file_name,
                work_dir_path=work_dir_path,
            )
            result = step_implementer._run_step()

            # # Expected results
            expected_step_result = StepResult(step_name='sign-container-image', sub_step_name='CurlPush',
                                              sub_step_implementer_name='CurlPush')
            expected_step_result.success = False
            expected_step_result.message = "Missing container-image-signature-name"
            self.assertEqual(expected_step_result.get_step_result(), result.get_step_result())
