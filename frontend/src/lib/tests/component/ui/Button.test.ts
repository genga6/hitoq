import { describe, it, expect } from "vitest";
import { render, fireEvent } from "@testing-library/svelte";
import Button from "$lib/components/ui/Button.svelte";

describe("Button Component", () => {
  it("renders with default props", () => {
    const { getByRole } = render(Button, { props: { children: "Click me" } });

    const button = getByRole("button");
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent("Click me");
  });

  it("applies variant classes correctly", () => {
    const { getByRole } = render(Button, {
      props: {
        variant: "primary",
        children: "Primary Button",
      },
    });

    const button = getByRole("button");
    expect(button).toHaveClass("btn-primary");
  });

  it("handles click events", async () => {
    let clicked = false;
    const handleClick = () => {
      clicked = true;
    };

    const { getByRole } = render(Button, {
      props: {
        onclick: handleClick,
        children: "Click me",
      },
    });

    const button = getByRole("button");
    await fireEvent.click(button);

    expect(clicked).toBe(true);
  });

  it("can be disabled", () => {
    const { getByRole } = render(Button, {
      props: {
        disabled: true,
        children: "Disabled",
      },
    });

    const button = getByRole("button");
    expect(button).toBeDisabled();
  });

  it("shows loading state", () => {
    const { getByRole } = render(Button, {
      props: {
        loading: true,
        children: "Loading...",
      },
    });

    const button = getByRole("button");
    expect(button).toBeDisabled();
    expect(button).toHaveClass("loading");
  });
});
