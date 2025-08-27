// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces

import "svelte/elements";
import type { BaseUser } from "$lib/types";

declare global {
  namespace App {
    interface Locals {
      user: BaseUser | null;
    }
  }
}

export {};
