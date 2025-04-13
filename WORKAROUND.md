# Workarounds for SentinelPC Development

This document outlines the current temporary workarounds in place for SentinelPC development due to ongoing issues. It should be updated as needed and removed once the root issues are resolved.

## Current Issue: CI Billing Problem

**Description:**

CI jobs are not running due to a billing problem with the CI service (GitHub Actions). The error message encountered is:

> "The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings."

**Impact:**

*   Automated CI workflows (e.g., linting, testing, building, releases) are not being executed.
*   Automated building and upload of `SentinelPC.exe` to GitHub Releases is currently disabled.
*   Code quality checks, automated testing and code deployment are not running.

**Status:**

*   **Investigating:** The billing issue is under investigation.
*   **Workarounds Active:** The workarounds listed below are being used to continue development until the CI problem is resolved.

## Temporary Workarounds

1.  **Local Development & Testing:**
    *   **Procedure:** Developers will primarily work on and test code locally.
    *   **Testing:** Unit tests and other tests must be run manually using the appropriate commands.
    *   **Commitment:** `git` should be used for version control with regular commits.
    * **Example**
        ```bash
        # Run unit test
        python -m unittest discover -s tests

        # Run Black Formatter
        black src tests

        #Run Flake8
        flake8 src tests
        ```
2.  **Manual Build:**
    *   **Procedure:** To create a distributable executable, use the `build_unified.py` script manually.
    *   **Steps:**
        1.  Navigate to the project root directory.
        2.  Run the build script:
            ```bash
            python build_unified.py
            ```
        3.  The `SentinelPC.exe` will be created in the output directory (`dist/`, likely).
        4. Manually test the `SentinelPC.exe` file to confirm it works correctly.
    * **Note:** This should also be done to verify that the exe runs correctly.
3.  **Manual Release (if required):**
    *   **Procedure:** If a release is needed, it must be created manually on GitHub Releases.
    *   **Steps:**
        1.  Go to the "Releases" section of the GitHub repository.
        2.  Click "Draft a new release".
        3.  Create a new release, add a tag (e.g. `v1.0.1`), and add release notes.
        4.  Upload the manually built `SentinelPC.exe` file as an asset.
    * **Note:** The upload should be done after running and verifying the `SentinelPC.exe`

## Next Steps

1.  **Resolve Billing Issue:** The first priority is to resolve the billing issue with the CI service.
    *   **Action:** Check the "Billing & plans" section in the GitHub account or organization settings and update or fix the payment method or increase the spending limit, as needed.
2.  **Re-enable CI:** After the billing issue is resolved, confirm that the CI workflows are re-enabled and running correctly.
3. **Rerun CI Jobs:** Once the billing is fixed, rerun the failed CI jobs to complete the automation process.
4.  **Remove Workarounds:** Once CI is back online, delete this `WORKAROUND.md` file.
5. **Test:** Once the CI is active, you will need to check if the process to generate the `SentinelPC.exe` is working correctly. You may need to manually run a release to check that the `SentinelPC.exe` is being uploaded to releases correctly.

## Contact

If you encounter any problems or need assistance, please contact the project owner.
