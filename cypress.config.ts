import { defineConfig } from "cypress";
import { configureAllureAdapterPlugins } from "@mmisty/cypress-allure-adapter/plugins";

export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      configureAllureAdapterPlugins(on, config);
      return config;
    },
    baseUrl: "https://www.saucedemo.com",
    viewportWidth: 1920,
    viewportHeight: 1080,
    video: true, // Native Cypress video kaydı
    screenshotOnRunFailure: true,
    env: {
      allure: true,
      allureResults: "allure-results"
    }
  },
});