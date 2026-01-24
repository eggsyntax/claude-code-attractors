import { Review, Comment, ReviewStatus, Project } from '../types/core.js';

/**
 * Manages code reviews and collaborative workflows
 *
 * This class handles the lifecycle of code reviews, from creation to approval,
 * and facilitates collaboration between team members through comments and discussions.
 */
export class ReviewManager {
  private reviews: Map<string, Review> = new Map();
  private activeDiscussions: Map<string, Set<string>> = new Map(); // reviewId -> userIds

  /**
   * Creates a new code review
   */
  async createReview(
    projectId: string,
    title: string,
    description: string,
    fileIds: string[],
    author: string,
    reviewers: string[] = []
  ): Promise<Review> {
    const review: Review = {
      id: this.generateId(),
      projectId,
      title,
      description,
      files: fileIds,
      status: 'draft',
      author,
      reviewers,
      comments: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.reviews.set(review.id, review);
    return review;
  }

  /**
   * Submits a review for evaluation (changes status from draft to pending)
   */
  async submitReview(reviewId: string): Promise<Review> {
    const review = this.reviews.get(reviewId);
    if (!review) {
      throw new Error(`Review ${reviewId} not found`);
    }

    if (review.status !== 'draft') {
      throw new Error(`Review ${reviewId} is not in draft status`);
    }

    review.status = 'pending';
    review.updatedAt = new Date();

    // TODO: Notify reviewers
    await this.notifyReviewers(review);

    return review;
  }

  /**
   * Adds a comment to a review
   */
  async addComment(
    reviewId: string,
    author: string,
    content: string,
    location?: any, // CodeLocation
    parentCommentId?: string
  ): Promise<Comment> {
    const review = this.reviews.get(reviewId);
    if (!review) {
      throw new Error(`Review ${reviewId} not found`);
    }

    const comment: Comment = {
      id: this.generateId(),
      reviewId,
      author,
      content,
      location,
      replies: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    if (parentCommentId) {
      // Find parent comment and add as reply
      const parentComment = this.findComment(review, parentCommentId);
      if (parentComment) {
        parentComment.replies.push(comment);
      }
    } else {
      review.comments.push(comment);
    }

    review.updatedAt = new Date();

    // Track active discussion participants
    if (!this.activeDiscussions.has(reviewId)) {
      this.activeDiscussions.set(reviewId, new Set());
    }
    this.activeDiscussions.get(reviewId)!.add(author);

    return comment;
  }

  /**
   * Updates review status (approve, reject, etc.)
   */
  async updateReviewStatus(
    reviewId: string,
    status: ReviewStatus,
    reviewer: string
  ): Promise<Review> {
    const review = this.reviews.get(reviewId);
    if (!review) {
      throw new Error(`Review ${reviewId} not found`);
    }

    if (!review.reviewers.includes(reviewer)) {
      throw new Error(`${reviewer} is not authorized to update this review`);
    }

    review.status = status;
    review.updatedAt = new Date();

    // TODO: Notify stakeholders about status change
    await this.notifyStatusChange(review, status, reviewer);

    return review;
  }

  /**
   * Gets all reviews for a project
   */
  getProjectReviews(projectId: string): Review[] {
    return Array.from(this.reviews.values())
      .filter(review => review.projectId === projectId);
  }

  /**
   * Gets reviews assigned to a specific reviewer
   */
  getReviewsForReviewer(reviewerId: string): Review[] {
    return Array.from(this.reviews.values())
      .filter(review => review.reviewers.includes(reviewerId));
  }

  /**
   * Gets active discussion participants for a review
   */
  getActiveDiscussionParticipants(reviewId: string): string[] {
    return Array.from(this.activeDiscussions.get(reviewId) || []);
  }

  private findComment(review: Review, commentId: string): Comment | null {
    // Search top-level comments
    for (const comment of review.comments) {
      if (comment.id === commentId) {
        return comment;
      }
      // Search replies recursively
      const found = this.findCommentInReplies(comment.replies, commentId);
      if (found) {
        return found;
      }
    }
    return null;
  }

  private findCommentInReplies(replies: Comment[], commentId: string): Comment | null {
    for (const reply of replies) {
      if (reply.id === commentId) {
        return reply;
      }
      const found = this.findCommentInReplies(reply.replies, commentId);
      if (found) {
        return found;
      }
    }
    return null;
  }

  private async notifyReviewers(review: Review): Promise<void> {
    // TODO: Implement notification system
    console.log(`Notifying reviewers for review ${review.id}: ${review.reviewers.join(', ')}`);
  }

  private async notifyStatusChange(
    review: Review,
    status: ReviewStatus,
    reviewer: string
  ): Promise<void> {
    // TODO: Implement status change notifications
    console.log(`Review ${review.id} status changed to ${status} by ${reviewer}`);
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }
}