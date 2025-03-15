import { Transport } from "@modelcontextprotocol/sdk/shared/transport.js";

function onClientError(error: Error) {
  console.error("Error from inspector client:", error);
}

function onServerError(error: Error) {
  console.error("Error from MCP server:", error);
}

export default function mcpProxy({
  transportToClient,
  transportToServer,
}: {
  transportToClient: Transport;
  transportToServer: Transport;
}) {
  let transportToClientClosed = false;
  let transportToServerClosed = false;

  transportToClient.onmessage = (message) => {
    console.log("Message from client to server:", JSON.stringify(message));
    transportToServer.send(message).catch(onServerError);
  };

  transportToServer.onmessage = (message) => {
    console.log("Message from server to client:", JSON.stringify(message));
    transportToClient.send(message).catch(onClientError);
  };

  transportToClient.onclose = () => {
    if (transportToServerClosed) {
      return;
    }

    transportToClientClosed = true;
    transportToServer.close().catch(onServerError);
  };

  transportToServer.onclose = () => {
    if (transportToClientClosed) {
      return;
    }
    transportToServerClosed = true;
    transportToClient.close().catch(onClientError);
  };

  transportToClient.onerror = onClientError;
  transportToServer.onerror = onServerError;
}
