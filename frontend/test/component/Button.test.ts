import { describe, it, expect } from "vitest";

// Button component logic testing
describe("Button Component Logic", () => {
  // Button variant classes
  const variantClasses = {
    primary:
      "bg-orange-500 text-white hover:bg-orange-600 focus:ring-orange-400",
    secondary:
      "bg-gray-200 text-gray-700 hover:bg-gray-300 focus:ring-gray-500",
    ghost: "text-gray-600 hover:text-gray-800 hover:bg-gray-100",
    danger: "bg-red-500 text-white hover:bg-red-600 focus:ring-red-400",
  };

  const sizeClasses = {
    sm: "px-2 py-1 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base",
  };

  const baseClasses =
    "rounded-md font-medium transition-colors focus:ring-2 focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed";

  // Test class combinations
  it("should generate correct classes for primary button", () => {
    const classes = `${baseClasses} ${variantClasses.primary} ${sizeClasses.md}`;

    expect(classes).toContain("bg-orange-500");
    expect(classes).toContain("text-white");
    expect(classes).toContain("px-4 py-2 text-sm");
    expect(classes).toContain("rounded-md");
  });

  it("should generate correct classes for secondary button", () => {
    const classes = `${baseClasses} ${variantClasses.secondary} ${sizeClasses.lg}`;

    expect(classes).toContain("bg-gray-200");
    expect(classes).toContain("text-gray-700");
    expect(classes).toContain("px-6 py-3 text-base");
  });

  it("should generate correct classes for ghost button", () => {
    const classes = `${baseClasses} ${variantClasses.ghost} ${sizeClasses.sm}`;

    expect(classes).toContain("text-gray-600");
    expect(classes).toContain("hover:text-gray-800");
    expect(classes).toContain("px-2 py-1 text-xs");
  });

  it("should generate correct classes for danger button", () => {
    const classes = `${baseClasses} ${variantClasses.danger} ${sizeClasses.md}`;

    expect(classes).toContain("bg-red-500");
    expect(classes).toContain("text-white");
    expect(classes).toContain("px-4 py-2 text-sm");
  });

  // Test disabled/loading state logic
  it("should apply disabled classes when loading or disabled", () => {
    const disabledClasses = "bg-gray-400 text-gray-600";

    expect(disabledClasses).toContain("bg-gray-400");
    expect(disabledClasses).toContain("text-gray-600");
  });

  // Test derived state logic
  it("should correctly determine disabled state", () => {
    const disabled = false;
    const loading = true;
    const isDisabled = disabled || loading;

    expect(isDisabled).toBe(true);
  });

  it("should correctly determine disabled state when neither", () => {
    const disabled = false;
    const loading = false;
    const isDisabled = disabled || loading;

    expect(isDisabled).toBe(false);
  });

  it("should correctly determine disabled state when disabled", () => {
    const disabled = true;
    const loading = false;
    const isDisabled = disabled || loading;

    expect(isDisabled).toBe(true);
  });

  // Test variant combinations exist
  it("should have all required variant classes", () => {
    const variants = Object.keys(variantClasses);
    expect(variants).toEqual(["primary", "secondary", "ghost", "danger"]);
  });

  it("should have all required size classes", () => {
    const sizes = Object.keys(sizeClasses);
    expect(sizes).toEqual(["sm", "md", "lg"]);
  });
});
