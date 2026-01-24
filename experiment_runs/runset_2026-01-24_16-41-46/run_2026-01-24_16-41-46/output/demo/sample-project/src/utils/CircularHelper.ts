// Intentional circular dependency to demonstrate detection
import { Application } from '../index';

export class CircularHelper {
  public static processApplication(app: any): void {
    console.log('Processing application');
    // This creates a circular dependency that our analyzer should detect
  }

  public static validateRequest(data: any): boolean {
    return data && typeof data === 'object';
  }
}