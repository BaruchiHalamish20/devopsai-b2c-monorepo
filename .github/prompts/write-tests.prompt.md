# Generate Unit Tests

Create comprehensive unit tests for the selected code or current file.

## Requirements

### Test Framework
- Use Jest for JavaScript/TypeScript
- Use pytest for Python
- Use the existing test framework in the project

### Test Coverage
Generate tests for:
- Happy path scenarios (expected inputs and outputs)
- Edge cases (empty inputs, null, undefined, boundary values)
- Error cases (invalid inputs, exceptions)
- Async operations (if applicable)

### Test Structure
- Use clear, descriptive test names following "should [expected behavior] when [condition]" pattern
- Group related tests with describe/context blocks
- Use proper setup/teardown (beforeEach, afterEach)
- Mock external dependencies (API calls, database, file system)

### Code Quality
- Each test should test ONE thing
- Tests should be independent (no shared state)
- Use meaningful variable names in tests
- Add comments for complex test scenarios

## Output

Provide:
1. Complete test file with all necessary imports
2. Proper mocking setup
3. At least 5-10 test cases covering different scenarios
4. Brief explanation of what each test validates

Place tests in the appropriate test directory following project conventions.
