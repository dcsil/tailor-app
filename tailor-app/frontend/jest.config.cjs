module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jest-fixed-jsdom',
  transform: {
    "^.+\\.(ts|tsx)$": "ts-jest",
    "^.+\\.(js|jsx)$": "babel-jest"
  },
  moduleNameMapper: {
    '\\.(gif|ttf|eot|svg|png)$': '<rootDir>/src/__mocks__/fileMock.js',
    '\\.(css|less|sass|scss)$': '<rootDir>/src/__mocks__/styleMock.js',
  },
  extensionsToTreatAsEsm: ['.ts', '.tsx'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx'],
  transformIgnorePatterns: [
    '/node_modules/(?!.*\\.mjs$)'
  ],
  moduleDirectories: ['node_modules', 'src'],
};