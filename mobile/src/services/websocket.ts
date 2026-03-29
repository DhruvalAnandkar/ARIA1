import { WS_URL, WS_RECONNECT_INTERVAL_MS } from "../constants/config";
import { getToken } from "../utils/storage";

type MessageHandler = (data: any) => void;

export class WSManager {
  private ws: WebSocket | null = null;
  private path: string;
  private onMessage: MessageHandler;
  private onStatusChange: (connected: boolean) => void;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private shouldReconnect = false;

  constructor(
    path: string,
    onMessage: MessageHandler,
    onStatusChange: (connected: boolean) => void
  ) {
    this.path = path;
    this.onMessage = onMessage;
    this.onStatusChange = onStatusChange;
  }

  async connect(queryParams?: Record<string, string>): Promise<void> {
    this.shouldReconnect = true;
    const token = await getToken();
    if (!token) return;

    const params = new URLSearchParams({ token, ...queryParams });
    const url = `${WS_URL}${this.path}?${params.toString()}`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.onStatusChange(true);
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.onMessage(data);
      } catch {
        console.error("Failed to parse WS message:", event.data);
      }
    };

    this.ws.onclose = () => {
      this.onStatusChange(false);
      this.scheduleReconnect(queryParams);
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  send(data: object): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect(): void {
    this.shouldReconnect = false;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.ws?.close();
    this.ws = null;
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  private scheduleReconnect(queryParams?: Record<string, string>): void {
    if (!this.shouldReconnect) return;
    this.reconnectTimer = setTimeout(() => {
      this.connect(queryParams);
    }, WS_RECONNECT_INTERVAL_MS);
  }
}
