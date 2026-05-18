//package com.bachelor.sensorserver;
//
//import org.springframework.stereotype.Component;
//import org.springframework.web.socket.*;
//import org.springframework.web.socket.handler.TextWebSocketHandler;
//
//@Component
//public class FaceHandler extends TextWebSocketHandler {
//
//    @Override
//    public void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
//        System.out.println("ARKit Face Data: " + message.getPayload());
//    }
//
//    @Override
//    public void afterConnectionEstablished(WebSocketSession session) {
//        System.out.println("ARKit verbunden");
//    }
//
//    @Override
//    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
//        System.out.println("ARKit getrennt");
//    }
//}