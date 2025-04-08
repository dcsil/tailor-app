Tailor is a cutting-edge Generative AI platform that automates the creation of personalized mood boards, transforming creative ideas into visually stunning collections with ease.

## Use cases
Below is a natural flow of the available use cases along with their descriptions:

1) **Text to mood board**: This core feature allows users to generate a mood board by simply typing in an aesthetic keyword (e.g., cottagecore, dark academia). Tailor's AI interprets the input and assembles a mood board that reflects the desired style.

2) **Mood board refinements**: After the initial mood board is generated, users can fine-tune it according to their preferences. The interactive editor allows for resizing, repositioning images, and removing any elements that don't fit the vision. Users can also add new, relevant images to the mood board by clicking the "Add" button to further personalize it.

3) **Image inspector panel**: The inspector panel provides detailed insights into each image on the board. Users can view key properties such as position, scale, description, and color palette, offering a deeper understanding of the elements contributing to the overall mood board.

4) **Analysis report**: Tailor's AI generates a comprehensive analysis of the mood board, highlighting key design elements like textures, colors, patterns, and the overall mood. This analysis can be refined and regenerated multiple times until the user is satisfied with the final report.

5) **Export**:Once the mood board is finalized, users can easily download the board along with its analysis (if applicable) to their device for further use or sharing.

6) **Mood boards collection**:  All generated mood boards are automatically saved to the user's Collections > Moodboards section. From here, users can view, manage, and delete boards as needed.

7) **Upload and navigating to uploads collection**: Users can upload company assets to Tailor’s cloud database. Tailor’s AI model pre-fills image properties such as description, class, and colors, making it easy to integrate these assets into mood boards that reflect the company’s branding. These uploaded assets can be managed from Collections > Uploads, where users can access, view, or delete them as required.

## Code quality

### Tools for measuring and enforcing code quality:
- #### Backend (Ruff and Pylint):

    #### Upon commit
    `ruff --fix --exit-non-zero-on-fix` is run. The `--fix` option utomatically fixes any linting issues it detects in the code. The `--exit-non-zero-on-fix` option ensures that if Ruff makes any changes to the code (i.e., fixes issues), the process will exit with a non-zero exit code, causing the commit to fail unless the changes are staged.
    The `ruff-format` hook focuses on correcting the format of the code (e.g., indentation, spacing, line length). 
    Here’s an improved version of the sentence:

    Ruff is a fast, all-in-one tool that combines linting and formatting, automatically fixes issues, and offers customization options. It seamlessly integrates with pre-commit hooks, ensuring code quality is maintained before changes are committed to the repository and CI jobs are triggered.

    #### On pull request (workflow run)
    `ruff check` and `ruff format --check` check if the code adheres to the linting or formatting standards, but do not fix any issues.
    `pylint --rcfile=.pylintrc` generates a detailed report to analyze code quality and code smells, and track improvements over time.
    It also provides a score (out of 10) for the code, which can be a good metric for tracking progress.
    A CI example run: https://github.com/dcsil/tailor-app/actions/runs/14338584008/job/40191946329?pr=75
  
   **Note:** The Pylint report identified a few minor style issues, such as too-many-positional-arguments, too-many-return-statements, and import-outside-toplevel. These can be safely ignored for now, as our primary focus for the MVP was on core functionality. Given that the overall score was high (9.8/10), we plan to address these stylistic concerns during future refactoring as needed.



- #### Frontend:

### Code coverage:

#### Design Goal
Our main goal for evaluating code coverage was to ensure that our backend, which contains our core business logic, was adequately tested. We implemented pytest-coverage-comment to manage our MVP's code coverage tracking. This lightweight, free, open-source solution generates coverage comments directly on PRs through GitHub Actions based on the reports created by pytest.

Since we introduced coverage tracking relatively late in the development process, we prioritized ease of setup and use. pytest-coverage-comment fit our needs well due to its straightforward implementation, seamless pytest integration, and lack of external service dependencies. While we considered alternatives like Codecov and Code Climate, their more sophisticated configurations and feature sets exceeded what we needed for our MVP at this stage. The primary limitations of our chosen solution are its minimal historical tracking capabilities, absence of visualization dashboards for trend analysis, and support limited to Python. However, these tradeoffs were acceptable given our current requirements and development phase.

#### Viewing Code Coverage Reports
Code coverage reports are added as comments to all PRs after the backend unit testing completes. The comment includes statements, misses and coverage percentage for backend python files. If there are misses, the comment also includes a reference to the lines with missing coverage. You can view an example Coverage Report at: https://github.com/dcsil/tailor-app/pull/75
