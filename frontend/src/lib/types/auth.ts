import type { BaseUser } from "./common";

export interface AuthenticatedState {
  isLoggedIn: true;
  user: BaseUser;
  userName: string;
}

export interface UnauthenticatedState {
  isLoggedIn: false;
  user: null;
  userName: null;
}

export type AuthState = AuthenticatedState | UnauthenticatedState;
