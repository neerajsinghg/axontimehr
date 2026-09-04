import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { App } from '../App';

describe('AxonTime HR App Shell', () => {
  it('renders application brand title', () => {
    render(<App />);
    expect(screen.getByText('AxonTime HR')).toBeInTheDocument();
  });
});
