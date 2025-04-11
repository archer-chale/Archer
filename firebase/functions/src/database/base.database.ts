import * as admin from 'firebase-admin';
export type CollectionName = 'traders' | 'messages';


// Custom error class
class DatabaseError extends Error {
  constructor(message: string, public code: string) {
    super(message);
    this.name = "DatabaseError";
  }
}

class BaseDatabaseService<T extends { id?: string }, C extends CollectionName> {
  protected collection: admin.firestore.CollectionReference;

  constructor(collectionName: string) {
    this.collection = admin.firestore().collection(collectionName);
  }

  protected handleError(operation: string, error: any): never {
    console.error(`${operation} - error:`, error);
    throw new DatabaseError(`Error in ${operation}: ${error.message}`, error.code || 'unknown');
  }

  async getAll(limit: number = 10, startAfter?: any): Promise<T[]> {
    try {
      let query = this.collection.limit(limit);
      if (startAfter) {
        query = query.startAfter(startAfter);
      }
      const querySnapshot = await query.get();
      return querySnapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() } as T));
    } catch (error) {
      this.handleError('getAll', error);
    }
  }

  async getOne(id: string): Promise<T | null> {
    try {
      const docSnap = await this.collection.doc(id).get();
      return docSnap.exists ? { id: docSnap.id, ...docSnap.data() } as T : null;
    } catch (error) {
      this.handleError('getOne', error);
    }
  }

  async create(data: Omit<T, 'id'>): Promise<T> {
    try {
      const now = admin.firestore.Timestamp.now();;
      const dataWithTimestamps = {
        ...data,
        createdAt: now,
        updatedAt: now
      };
      const newDocRef = await this.collection.add(dataWithTimestamps);
      return { id: newDocRef.id, ...dataWithTimestamps } as unknown as T;
    } catch (error) {
      this.handleError('create', error);
    }
  }

  async update(id: string, data: Partial<T>): Promise<T> {
    try {
      const now = admin.firestore.Timestamp.now();;
      const dataWithTimestamp = {
        ...data,
        updatedAt: now
      };
      await this.collection.doc(id).set(dataWithTimestamp, { merge: true });
      return { id, ...dataWithTimestamp } as unknown as T;
    } catch (error) {
      this.handleError('update', error);
    }
  }
  async remove(id: string): Promise<boolean> {
    try {
      await this.collection.doc(id).delete();
      return true;
    } catch (error) {
      this.handleError('remove', error);
    }
  }

  async getAllByUserId(userId: string, limit: number = 10, startAfter?: any): Promise<T[]> {
    try {
      let query = this.collection.where('userId', '==', userId).limit(limit);
      if (startAfter) {
        query = query.startAfter(startAfter);
      }
      const querySnapshot = await query.get();
      return querySnapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() } as T));
    } catch (error) {
      this.handleError('getAllByUserId', error);
    }
  }

  async getOneByUserId(userId: string): Promise<T | null> {
    try {
      const querySnapshot = await this.collection.where('userId', '==', userId).limit(1).get();
      if (!querySnapshot.empty) {
        const doc = querySnapshot.docs[0];
        return { id: doc.id, ...doc.data() } as T;
      }
      return null;
    } catch (error) {
      this.handleError('getOneByUserId', error);
    }
  }
  async createWithUserId(userId: string, data: Omit<T, 'id' | 'userId'>): Promise<T> {
    try {
      const now = admin.firestore.Timestamp.now();;
      const dataWithTimestamps = {
        ...data,
        userId,
        createdAt: now,
        updatedAt: now
      };
      const newDocRef = await this.collection.add(dataWithTimestamps);
      return { id: newDocRef.id, ...dataWithTimestamps } as unknown as T;
    } catch (error) {
      this.handleError('createWithUserId', error);
    }
  }

  async updateByUserId(userId: string, data: Partial<T>): Promise<T | null> {
    try {
      const querySnapshot = await this.collection.where('userId', '==', userId).limit(1).get();
      if (!querySnapshot.empty) {
        const doc = querySnapshot.docs[0];
        const now = admin.firestore.Timestamp.now();;
        const dataWithTimestamp = {
          ...data,
          updatedAt: now
        };
        await doc.ref.set(dataWithTimestamp, { merge: true });
        return { id: doc.id, ...dataWithTimestamp } as unknown as T;
      }
      return null;
    } catch (error) {
      this.handleError('updateByUserId', error);
    }
  }

  async updateOrCreateByUserId(userId: string, data: Omit<T, 'id'>): Promise<T> {
    try {
      const querySnapshot = await this.collection.where('userId', '==', userId).limit(1).get();
      const now = admin.firestore.Timestamp.now();;
      if (!querySnapshot.empty) {
        const doc = querySnapshot.docs[0];
        const dataWithTimestamp = {
          ...data,
          updatedAt: now
        };
        await doc.ref.set(dataWithTimestamp, { merge: true });
        return { id: doc.id, ...dataWithTimestamp } as unknown as T;
      } else {
        const dataWithTimestamps = {
          ...data,
          userId,
          createdAt: now,
          updatedAt: now
        };
        const newDocRef = await this.collection.add(dataWithTimestamps);
        return { id: newDocRef.id, ...dataWithTimestamps } as unknown as T;
      }
    } catch (error) {
      this.handleError('updateOrCreateByUserId', error);
    }
  }

  async removeByUserId(userId: string): Promise<boolean> {
    try {
      const querySnapshot = await this.collection.where('userId', '==', userId).get();
      const batch = admin.firestore().batch();
      querySnapshot.docs.forEach((doc) => {
        batch.delete(doc.ref);
      });
      await batch.commit();
      return true;
    } catch (error) {
      this.handleError('removeByUserId', error);
    }
  }

}

export default BaseDatabaseService;