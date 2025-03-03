import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, act } from "@testing-library/react";

// Mock the modules before importing App
jest.mock("../utils/env");
jest.mock("../components/Chat", () => {
  return function MockChat() {
    return <div data-testid="chat-component">Chat Component</div>;
  };
});

// Mock the fetch API
(window as any).fetch = jest.fn(() => 
    Promise.resolve({
      json: () => Promise.resolve({ status: 'ok' }),
    })
);

// Import App after the mocks are set up
import App from "../App";

describe('App Component', () => {
  test('demo', () => {
    expect(true).toBe(true);
  });

  test("Renders the main page", async () => {
    await act(async () => {
      render(<App />);
    });

    expect(screen.getByText("Hello World!")).toBeInTheDocument();
    // Test if the mocked Chat component is present
    expect(screen.getByTestId("chat-component")).toBeInTheDocument();
  });
});