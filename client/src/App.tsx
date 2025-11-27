import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import CoinSelector from "./pages/CoinSelector";
import MultiCoinMonitor from "./pages/MultiCoinMonitor";
import RotationSettings from "./pages/RotationSettings";
import DeploymentStatus from "./pages/DeploymentStatus";
import TradeHistory from "./pages/TradeHistory";
import RiskAnalysis from "./pages/RiskAnalysis";

function Router() {
  return (
    <Switch>
      <Route path={"/"} component={Home} />
      <Route path={"/coin-selector"} component={CoinSelector} />
      <Route path={"/multi-coin-monitor"} component={MultiCoinMonitor} />
      <Route path={"/rotation-settings"} component={RotationSettings} />
      <Route path={"/deployment-status"} component={DeploymentStatus} />
      <Route path={"/history"} component={TradeHistory} />
      <Route path={"/risk-analysis"} component={RiskAnalysis} />
      <Route path={"/404"} component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="light"
        // switchable
      >
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
