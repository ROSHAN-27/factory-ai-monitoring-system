import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { ErrorBoundary } from "../ui/ErrorBoundary";
import { Panel } from "../ui/Panel";

type WidgetFrameProps = {
  title: string;
  action?: ReactNode;
  children: ReactNode;
};

export function WidgetFrame({ title, action, children }: WidgetFrameProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.22 }}>
      <Panel title={title} action={action}>
        <ErrorBoundary>{children}</ErrorBoundary>
      </Panel>
    </motion.div>
  );
}
