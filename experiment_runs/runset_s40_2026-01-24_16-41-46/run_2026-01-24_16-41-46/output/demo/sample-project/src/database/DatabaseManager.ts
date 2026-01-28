import { User, CreateUserRequest } from '../types/User';

// Singleton pattern implementation
export class DatabaseManager {
  private static instance: DatabaseManager;
  private connections: Map<string, any> = new Map();

  private constructor() {
    // Private constructor for singleton
    this.initializeConnections();
  }

  public static getInstance(): DatabaseManager {
    if (!DatabaseManager.instance) {
      DatabaseManager.instance = new DatabaseManager();
    }
    return DatabaseManager.instance;
  }

  private initializeConnections(): void {
    // Simulate database connections
    this.connections.set('primary', { host: 'localhost', port: 5432 });
    this.connections.set('replica', { host: 'replica.localhost', port: 5432 });
  }

  public async createUser(userData: CreateUserRequest): Promise<User> {
    // Simulate database operation
    const user: User = {
      id: Math.random().toString(36).substr(2, 9),
      email: userData.email,
      name: userData.name,
      createdAt: new Date(),
      preferences: userData.preferences
    };

    console.log('Creating user in database:', user.id);
    return user;
  }

  public async getAllUsers(): Promise<User[]> {
    // Simulate fetching users
    console.log('Fetching all users from database');
    return [];
  }

  public async getUserById(id: string): Promise<User | null> {
    console.log('Fetching user by ID:', id);
    return null;
  }

  public async updateUser(id: string, userData: Partial<CreateUserRequest>): Promise<User> {
    console.log('Updating user:', id);
    // Simulate update operation
    return {
      id,
      email: userData.email || '',
      name: userData.name || '',
      createdAt: new Date(),
      preferences: userData.preferences
    };
  }

  // Factory method for different connection types
  public getConnection(type: 'primary' | 'replica' = 'primary') {
    return this.connections.get(type);
  }
}