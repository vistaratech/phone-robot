// WebSocket client for the PhoneBot onboard server (robot/server.py).
export const N_JOINTS = 13;

export type RobotState = {
  t: number; q: number[]; dq: number[]; load: number[];
  torque: boolean; pad: { axes: number[]; buttons: number[] } | null;
};

export class PhoneBotClient {
  private ws?: WebSocket;
  onState: (s: RobotState) => void = () => {};
  onStatus: (connected: boolean) => void = () => {};

  connect(url: string) {
    this.ws = new WebSocket(url);
    this.ws.onopen = () => this.onStatus(true);
    this.ws.onclose = () => this.onStatus(false);
    this.ws.onerror = () => this.onStatus(false);
    this.ws.onmessage = (e) => {
      try {
        const m = JSON.parse(e.data as string);
        if (m.type === 'state') this.onState(m as RobotState);
      } catch {}
    };
  }
  disconnect() { this.ws?.close(); }
  private send(o: object) {
    if (this.ws?.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(o));
  }
  setTorque(enable: boolean) { this.send({ type: 'torque', enable }); }
  sendJoints(q: number[]) {
    if (q.length === N_JOINTS) this.send({ type: 'cmd', q });
  }
}
