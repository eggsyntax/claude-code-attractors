import express from 'express';
import { UserService } from './services/UserService';
import { DatabaseManager } from './database/DatabaseManager';
import { AuthMiddleware } from './middleware/AuthMiddleware';

// Demonstration of various patterns for our analyzer to detect
export class Application {
  private app: express.Application;
  private userService: UserService;
  private dbManager: DatabaseManager;

  constructor() {
    this.app = express();
    this.userService = new UserService();
    this.dbManager = DatabaseManager.getInstance(); // Singleton pattern
    this.setupMiddleware();
    this.setupRoutes();
  }

  private setupMiddleware(): void {
    this.app.use(express.json());
    this.app.use(AuthMiddleware.authenticate);
  }

  private setupRoutes(): void {
    this.app.get('/users', async (req, res) => {
      try {
        const users = await this.userService.getAllUsers();
        res.json(users);
      } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
      }
    });

    this.app.post('/users', async (req, res) => {
      try {
        const newUser = await this.userService.createUser(req.body);
        res.status(201).json(newUser);
      } catch (error) {
        res.status(400).json({ error: 'Bad request' });
      }
    });
  }

  public start(port: number = 3000): void {
    this.app.listen(port, () => {
      console.log(`Server running on port ${port}`);
    });
  }
}

// Circular dependency example (intentional code smell)
import { CircularHelper } from './utils/CircularHelper';

if (require.main === module) {
  const app = new Application();
  app.start();
}