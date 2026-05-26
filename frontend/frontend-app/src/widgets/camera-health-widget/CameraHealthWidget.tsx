import { CameraHealthPanel } from "../../features/camera-health/components/CameraHealthPanel";
import { WidgetFrame } from "../../shared/layouts/WidgetFrame";
import type { CameraHealth } from "../../shared/types/domain";

export function CameraHealthWidget({ cameras }: { cameras: CameraHealth[] }) {
  return (
    <WidgetFrame title="Camera Health">
      <CameraHealthPanel cameras={cameras} />
    </WidgetFrame>
  );
}
