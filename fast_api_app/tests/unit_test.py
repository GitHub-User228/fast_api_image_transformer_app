#!/usr/local/bin/python3

import io
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import unittest
from PIL import Image
from fastapi import Response
from fastapi.testclient import TestClient

from app.main import app
from fast_api_project.config.path_config import path_vars
from fast_api_project.utils.common import read_yaml, get_response
from fast_api_project.utils.limiters import global_limiter, ip_limiter


class TestFastAPIApp(unittest.TestCase):
    """
    Test suite for the FastAPI application.

    Attributes:
        invalid_tests (dict):
            A dictionary containing invalid test cases for the FastAPI
            application.
    """

    def setUp(self):
        """
        Sets up the test environment by overriding the global and IP
        limiters, and loads the invalid test cases from a YAML file.
        """
        app.dependency_overrides[global_limiter] = lambda: None
        app.dependency_overrides[ip_limiter] = lambda: None
        self.invalid_tests = read_yaml(
            Path(f"{path_vars.app_root_path}/tests/invalid_tests.yaml")
        )

    def tearDown(self):
        """
        Clears the dependency overrides for the FastAPI application.
        """
        app.dependency_overrides.clear()

    def _test_valid(self, client: TestClient) -> None:
        """
        Test a valid response from the FastAPI application.

        Args:
            client (TestClient):
                The FastAPI test client instance.
        """
        response = get_response(client=client)
        # Check if the response is valid
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/png")
        # Check if the response content is a valid PNG image
        image = Image.open(io.BytesIO(response.content))
        self.assertEqual(image.format, "PNG")
        self.assertEqual(image.mode, "RGB")

    def _sub_test_invalid(
        self,
        client: TestClient,
        param_name: str,
        invalid_value: bytes | str | int,
        expected_status: int,
        expected_message: str,
        is_path_value: bool = True,
        check_msg: bool = False,
    ) -> None:
        """
        Performs an invalid test for the FastAPI application.

        Args:
            client (TestClient):
                The test client to use for the request.
            param_name (str):
                The name of the parameter to test with an invalid value.
            invalid_value (bytes | str | int):
                The invalid value to use for the parameter.
            expected_status (int):
                The expected HTTP status code for the response.
            expected_message (str):
                The expected part of an error message in the response.
            is_path_value (bool, default True):
                Whether the invalid value is a file path.
            check_msg (bool, default False):
                Whether to check the error message in the response.
        """
        response = self._get_invalid_response(
            client=client,
            param_name=param_name,
            invalid_value=invalid_value,
            is_path_value=is_path_value,
        )
        self._validate_invalid_response(
            response=response,
            expected_status=expected_status,
            expected_message=expected_message,
            check_msg=check_msg,
        )

    def _get_invalid_response(
        self,
        client: TestClient,
        param_name: str,
        invalid_value: bytes | str | int,
        is_path_value: bool,
    ) -> Response:
        """
        Sends a request to the FastAPI application with the provided
        invalid value for the specified parameter.

        Args:
            client (TestClient):
                The test client to use for the request.
            param_name (str):
                The name of the parameter to test with an invalid value.
            invalid_value (bytes | str | int):
                The invalid value to use for the parameter.
            is_path_value (bool):
                Whether the invalid value is a file path.

        Returns:
            Response:
                The response from the FastAPI application.
        """
        if (param_name in ["image_file", "prompt_file"]) and is_path_value:
            return get_response(
                client=client, **{param_name: Path(invalid_value)}
            )
        return get_response(client=client, **{param_name: invalid_value})

    def _validate_invalid_response(
        self, response, expected_status, expected_message, check_msg
    ) -> None:
        """
        Validates the response from the FastAPI application

        Args:
            response (Response):
                The response from the FastAPI application.
            expected_status (int):
                The expected status code of the response.
            expected_message (str):
                The expected part of an error message in the response.
            check_msg (bool):
                Whether to check the error message in the response.

        Raises:
            AssertionError:
                If the status code or error message does not match
                the expected values.
        """
        self.assertEqual(response.status_code, expected_status)
        if check_msg:
            self.assertIn(
                expected_message, response.json()["detail"][0]["msg"]
            )
        else:
            self.assertIn(expected_message, response.json()["detail"])

    def _test_invalid(self, client: TestClient) -> None:
        """
        Tests invalid input parameters for the FastAPI application.

        Args:
            client (TestClient):
                The test client to use for the request.
        """
        for test_name, kwargs in self.invalid_tests.items():
            with self.subTest(test_name=test_name):
                self._sub_test_invalid(client=client, **kwargs)

    def test(self):
        """
        Runs the valid and invalid test cases for the FastAPI
        application.

        Args:
            client (TestClient):
                The test client to use for the requests.
        """
        with TestClient(app) as client:
            # Valid test case
            with self.subTest(test_name="valid_test"):
                self._test_valid(client=client)
            # Invalid test cases
            with self.subTest(test_name="invalid_tests"):
                self._test_invalid(client=client)


if __name__ == "__main__":
    unittest.main()
