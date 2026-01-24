import { DatabaseManager } from '../database/DatabaseManager';
import { User, CreateUserRequest } from '../types/User';
import { ValidationHelper } from '../utils/ValidationHelper';

// Observer pattern implementation
export interface UserServiceObserver {
  onUserCreated(user: User): void;
  onUserUpdated(user: User): void;
}

export class UserService {
  private observers: UserServiceObserver[] = [];
  private dbManager: DatabaseManager;

  constructor() {
    this.dbManager = DatabaseManager.getInstance();
  }

  // High complexity method for analysis
  public async createUser(userData: CreateUserRequest): Promise<User> {
    if (!ValidationHelper.validateEmail(userData.email)) {
      throw new Error('Invalid email');
    }

    if (!ValidationHelper.validatePassword(userData.password)) {
      throw new Error('Invalid password');
    }

    // Nested complexity for demonstration
    if (userData.preferences) {
      if (userData.preferences.notifications) {
        if (userData.preferences.notifications.email) {
          if (userData.preferences.notifications.email.frequency) {
            // Deep nesting - complexity hotspot
            console.log('Setting email notification frequency');
          }
        }
      }
    }

    const user = await this.dbManager.createUser(userData);

    // Notify observers (Observer pattern)
    this.observers.forEach(observer => observer.onUserCreated(user));

    return user;
  }

  public async getAllUsers(): Promise<User[]> {
    return this.dbManager.getAllUsers();
  }

  public async getUserById(id: string): Promise<User | null> {
    return this.dbManager.getUserById(id);
  }

  // Duplicate code pattern (code smell)
  public async updateUser(id: string, userData: Partial<CreateUserRequest>): Promise<User> {
    if (userData.email && !ValidationHelper.validateEmail(userData.email)) {
      throw new Error('Invalid email');
    }

    if (userData.password && !ValidationHelper.validatePassword(userData.password)) {
      throw new Error('Invalid password');
    }

    const user = await this.dbManager.updateUser(id, userData);
    this.observers.forEach(observer => observer.onUserUpdated(user));

    return user;
  }

  // Observer pattern methods
  public addObserver(observer: UserServiceObserver): void {
    this.observers.push(observer);
  }

  public removeObserver(observer: UserServiceObserver): void {
    const index = this.observers.indexOf(observer);
    if (index > -1) {
      this.observers.splice(index, 1);
    }
  }
}