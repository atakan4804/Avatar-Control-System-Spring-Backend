package com.bachelor.sensorserver;

import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.io.IOException;
import java.time.Instant;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

public class SensorHandler extends TextWebSocketHandler {

    // Speichert alle verbundenen Clients (Unity + Browser)
    private final Set<WebSocketSession> sessions =
            Collections.synchronizedSet(new HashSet<>());

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        sessions.add(session);

        String origin = session.getHandshakeHeaders().getOrigin();
        String ua = session.getHandshakeHeaders().getFirst("User-Agent");
        String host = session.getHandshakeHeaders().getFirst("Host");
        String remote = session.getRemoteAddress() != null ? session.getRemoteAddress().toString() : "unknown";

        System.out.println("WS verbunden"
                + " | id=" + session.getId()
                + " | remote=" + remote
                + " | host=" + host
                + " | origin=" + origin
                + " | ua=" + (ua != null ? ua : "-"));
    }

    @Override
    public void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        String payload = message.getPayload();

        // Eingehende Daten + Metadaten
        String remote = session.getRemoteAddress() != null ? session.getRemoteAddress().toString() : "unknown";
        System.out.println("WS msg"
                + " | id=" + session.getId()
                + " | remote=" + remote
                + " | ts=" + Instant.now().toEpochMilli()
                + " | bytes=" + (payload != null ? payload.length() : 0)
                + " | payloadLength=" + (payload != null ? payload.length() : 0));

        // An alle verbundenen Clients weiterleiten
        broadcastToAll(payload);
    }

    @Override
    public void handleTransportError(WebSocketSession session, Throwable exception) {
        String remote = session.getRemoteAddress() != null ? session.getRemoteAddress().toString() : "unknown";

        System.out.println("WS transport error"
                + " | id=" + session.getId()
                + " | remote=" + remote
                + " | msg=" + (exception != null ? exception.getMessage() : "null"));

        if (exception != null) {
            exception.printStackTrace(System.out);
        }
    }

    private void broadcastToAll(String message) {
        TextMessage out = new TextMessage(message == null ? "" : message);

        synchronized (sessions) {
            Set<WebSocketSession> toRemove = new HashSet<>();

            for (WebSocketSession s : sessions) {
                if (s == null || !s.isOpen()) {
                    toRemove.add(s);
                    continue;
                }

                try {
                    s.sendMessage(out);
                } catch (IOException ex) {
                    System.out.println("⚠WS send failed | id=" + s.getId() + " | msg=" + ex.getMessage());
                    toRemove.add(s);
                }
            }

            sessions.removeAll(toRemove);
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        sessions.remove(session);

        String remote = session.getRemoteAddress() != null ? session.getRemoteAddress().toString() : "unknown";
        int code = status != null ? status.getCode() : -1;
        String reason = status != null ? status.getReason() : "-";

        System.out.println("WS getrennt"
                + " | id=" + session.getId()
                + " | remote=" + remote
                + " | code=" + code
                + " | reason=" + reason);
    }
}