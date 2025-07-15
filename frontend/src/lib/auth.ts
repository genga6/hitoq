import { PUBLIC_API_BASE_URL } from "$env/static/public";

const API_BASE_URL = PUBLIC_API_BASE_URL;

export const redirectToTwitterLogin = () => {
  window.location.href = `${API_BASE_URL}/auth/login/twitter`;
};
