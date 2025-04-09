import * as Sentry from "@sentry/react";
import { useEffect } from "react";
import {
  createRoutesFromChildren,
  matchRoutes,
  useLocation,
  useNavigationType,
} from "react-router-dom";

Sentry.init({
  dsn: "https://e19ed4608eaae0df1e374a412d41af5c@o4508887891836928.ingest.us.sentry.io/4508887910318080",
  integrations: [
    // See docs for support of different versions of variation of react router
    // https://docs.sentry.io/platforms/javascript/guides/react/configuration/integrations/react-router/
    // Sentry.reactRouterV6BrowserTracingIntegration({
    //   useEffect,
    //   useLocation,
    //   useNavigationType,
    //   createRoutesFromChildren,
    //   matchRoutes,
    // }),
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],

  // Tracing
  tracesSampleRate: 1.0, //  Capture 100% of the transactions

  // Set `tracePropagationTargets` to control for which URLs trace propagation should be enabled
  tracePropagationTargets: ["localhost", /^https:\/\/yourserver\.io\/api/],

  // Session Replay
  replaysSessionSampleRate: 0.1, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
  replaysOnErrorSampleRate: 1.0, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
});
