import { EventEmitter } from 'events';
import WebSocket from 'ws';
import { Review, Comment } from '../types/core.js';

/**
 * Real-time collaboration hub using WebSockets
 *
 * Handles real-time communication between collaborators, including:
 * - Live comment updates
 * - Presence awareness (who's viewing what)
 * - Real-time review status changes
 * - Collaborative editing indicators
 */
export class CollaborationHub extends EventEmitter {
  private server?: WebSocket.Server;
  private connections: Map<string, UserConnection> = new Map();
  private reviewPresence: Map<string, Set<string>> = new Map(); // reviewId -> userIds

  interface UserConnection {
    ws: WebSocket;
    userId: string;
    currentReview?: string;
    lastActivity: Date;
  }

  /**
   * Initializes the WebSocket server for real-time collaboration
   */
  initialize(port: number = 8080): void {
    this.server = new WebSocket.Server({ port });
    console.log(`Collaboration hub started on port ${port}`);

    this.server.on('connection', (ws: WebSocket) => {
      this.handleNewConnection(ws);
    });

    // Clean up inactive connections every 30 seconds
    setInterval(() => this.cleanupInactiveConnections(), 30000);
  }

  /**
   * Broadcasts a comment update to all participants in a review
   */
  broadcastCommentUpdate(reviewId: string, comment: Comment): void {
    const participants = this.reviewPresence.get(reviewId) || new Set();
    const message = {
      type: 'comment_update',
      reviewId,
      comment,
      timestamp: new Date().toISOString()
    };

    for (const userId of participants) {
      const connection = this.connections.get(userId);
      if (connection && connection.ws.readyState === WebSocket.OPEN) {
        connection.ws.send(JSON.stringify(message));
      }
    }

    this.emit('comment_broadcasted', { reviewId, comment, participantCount: participants.size });
  }

  /**
   * Broadcasts review status changes
   */
  broadcastReviewStatusChange(review: Review): void {
    const participants = this.reviewPresence.get(review.id) || new Set();
    const message = {
      type: 'review_status_change',
      reviewId: review.id,
      status: review.status,
      updatedAt: review.updatedAt.toISOString()
    };

    for (const userId of participants) {
      const connection = this.connections.get(userId);
      if (connection && connection.ws.readyState === WebSocket.OPEN) {
        connection.ws.send(JSON.stringify(message));
      }
    }
  }

  /**
   * Notifies participants about who's currently viewing a review
   */
  broadcastPresenceUpdate(reviewId: string): void {
    const participants = Array.from(this.reviewPresence.get(reviewId) || []);
    const message = {
      type: 'presence_update',
      reviewId,
      participants,
      timestamp: new Date().toISOString()
    };

    for (const userId of participants) {
      const connection = this.connections.get(userId);
      if (connection && connection.ws.readyState === WebSocket.OPEN) {
        connection.ws.send(JSON.stringify(message));
      }
    }
  }

  /**
   * Gets currently active participants for a review
   */
  getActiveParticipants(reviewId: string): string[] {
    return Array.from(this.reviewPresence.get(reviewId) || []);
  }

  /**
   * Gets total number of active connections
   */
  getConnectionCount(): number {
    return this.connections.size;
  }

  private handleNewConnection(ws: WebSocket): void {
    let userId: string | null = null;

    ws.on('message', (data: WebSocket.Data) => {
      try {
        const message = JSON.parse(data.toString());
        this.handleMessage(ws, message, userId);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        ws.send(JSON.stringify({ type: 'error', message: 'Invalid message format' }));
      }
    });

    ws.on('close', () => {
      if (userId) {
        this.handleDisconnection(userId);
      }
    });

    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
      if (userId) {
        this.handleDisconnection(userId);
      }
    });
  }

  private handleMessage(ws: WebSocket, message: any, userId: string | null): void {
    switch (message.type) {
      case 'authenticate':
        userId = message.userId;
        this.connections.set(userId, {
          ws,
          userId,
          lastActivity: new Date()
        });
        ws.send(JSON.stringify({ type: 'authenticated', userId }));
        break;

      case 'join_review':
        if (userId && message.reviewId) {
          this.handleJoinReview(userId, message.reviewId);
        }
        break;

      case 'leave_review':
        if (userId && message.reviewId) {
          this.handleLeaveReview(userId, message.reviewId);
        }
        break;

      case 'typing_indicator':
        if (userId && message.reviewId) {
          this.handleTypingIndicator(userId, message.reviewId, message.isTyping);
        }
        break;

      case 'ping':
        if (userId) {
          const connection = this.connections.get(userId);
          if (connection) {
            connection.lastActivity = new Date();
            ws.send(JSON.stringify({ type: 'pong' }));
          }
        }
        break;

      default:
        ws.send(JSON.stringify({ type: 'error', message: 'Unknown message type' }));
    }
  }

  private handleJoinReview(userId: string, reviewId: string): void {
    const connection = this.connections.get(userId);
    if (!connection) return;

    // Leave current review if any
    if (connection.currentReview) {
      this.handleLeaveReview(userId, connection.currentReview);
    }

    // Join new review
    connection.currentReview = reviewId;

    if (!this.reviewPresence.has(reviewId)) {
      this.reviewPresence.set(reviewId, new Set());
    }
    this.reviewPresence.get(reviewId)!.add(userId);

    // Notify user and broadcast presence update
    connection.ws.send(JSON.stringify({
      type: 'joined_review',
      reviewId
    }));

    this.broadcastPresenceUpdate(reviewId);
    this.emit('user_joined_review', { userId, reviewId });
  }

  private handleLeaveReview(userId: string, reviewId: string): void {
    const connection = this.connections.get(userId);
    if (!connection) return;

    const participants = this.reviewPresence.get(reviewId);
    if (participants) {
      participants.delete(userId);
      if (participants.size === 0) {
        this.reviewPresence.delete(reviewId);
      }
    }

    connection.currentReview = undefined;
    this.broadcastPresenceUpdate(reviewId);
    this.emit('user_left_review', { userId, reviewId });
  }

  private handleTypingIndicator(userId: string, reviewId: string, isTyping: boolean): void {
    const participants = this.reviewPresence.get(reviewId);
    if (!participants || !participants.has(userId)) return;

    const message = {
      type: 'typing_indicator',
      reviewId,
      userId,
      isTyping,
      timestamp: new Date().toISOString()
    };

    // Broadcast to other participants (not the sender)
    for (const participantId of participants) {
      if (participantId !== userId) {
        const connection = this.connections.get(participantId);
        if (connection && connection.ws.readyState === WebSocket.OPEN) {
          connection.ws.send(JSON.stringify(message));
        }
      }
    }
  }

  private handleDisconnection(userId: string): void {
    const connection = this.connections.get(userId);
    if (!connection) return;

    if (connection.currentReview) {
      this.handleLeaveReview(userId, connection.currentReview);
    }

    this.connections.delete(userId);
    this.emit('user_disconnected', { userId });
  }

  private cleanupInactiveConnections(): void {
    const now = new Date();
    const timeout = 5 * 60 * 1000; // 5 minutes

    for (const [userId, connection] of this.connections) {
      const timeSinceActivity = now.getTime() - connection.lastActivity.getTime();

      if (timeSinceActivity > timeout || connection.ws.readyState !== WebSocket.OPEN) {
        console.log(`Cleaning up inactive connection for user ${userId}`);
        this.handleDisconnection(userId);
      }
    }
  }

  /**
   * Gracefully shuts down the collaboration hub
   */
  shutdown(): void {
    if (this.server) {
      this.server.close();
      console.log('Collaboration hub shut down');
    }
  }
}