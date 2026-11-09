import "@/App.css";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Show, SignIn, SignUp } from "@clerk/react";
import ClerkAuthProvider from "@/components/auth/ClerkAuthProvider";
import { Toaster } from "@/components/ui/sonner";
import AppShell from "@/components/layout/AppShell";
import Landing from "@/pages/Landing";
import Dashboard from "@/pages/Dashboard";
import Studio from "@/pages/Studio";
import ModelStudio from "@/pages/ModelStudio";
import BackgroundRemoval from "@/pages/BackgroundRemoval";
import Projects from "@/pages/Projects";
import ProjectDetail from "@/pages/ProjectDetail";
import History from "@/pages/History";
import Billing from "@/pages/Billing";
import AuthLayout from "@/pages/AuthLayout";

const Protected = ({ children }) => (
  <>
    <Show when="signed-in">{children}</Show>
    <Show when="signed-out"><Navigate to="/sign-in" replace /></Show>
  </>
);

function App() {
  return (
    <BrowserRouter>
      <ClerkAuthProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/sign-in/*" element={<AuthLayout><SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" withSignUp /></AuthLayout>} />
          <Route path="/sign-up/*" element={<AuthLayout><SignUp routing="path" path="/sign-up" signInUrl="/sign-in" /></AuthLayout>} />
          <Route path="/app" element={<Protected><AppShell /></Protected>}>
            <Route index element={<Dashboard />} />
            <Route path="studio" element={<Studio />} />
            <Route path="model" element={<ModelStudio />} />
            <Route path="background" element={<BackgroundRemoval />} />
            <Route path="projects" element={<Projects />} />
            <Route path="projects/:id" element={<ProjectDetail />} />
            <Route path="history" element={<History />} />
            <Route path="billing" element={<Billing />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster position="bottom-right" richColors />
      </ClerkAuthProvider>
    </BrowserRouter>
  );
}

export default App;
