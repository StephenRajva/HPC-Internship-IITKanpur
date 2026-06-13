#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int main(int argc, char *argv[]) {
    int rank, size, N;
    int *data = NULL;

    // 1. Initialize MPI environment
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // 2. Check for correct command line arguments
    if (argc != 2) {
        if (rank == 0) {
            printf("Error: Please provide N.\nUsage: mpirun -np <processes> %s <N>\n", argv[0]);
        }
        MPI_Finalize();
        return 1;
    }

    // Convert string argument to integer
    N = atoi(argv[1]);

    // Check if N is valid
    if (N <= 0) {
        if (rank == 0) printf("Error: N must be a positive integer.\n");
        MPI_Finalize();
        return 1;
    }

    // 3. Ensure we have an even number of processes for perfect pairing
    if (size % 2 != 0) {
        if (rank == 0) {
            printf("Error: This logic requires an EVEN number of processes (P/2 pairs).\n");
        }
        MPI_Finalize();
        return 1;
    }

    // 4. Dynamically allocate the array
    data = (int *)malloc(N * sizeof(int));
    if (data == NULL) {
        printf("Process %d failed to allocate memory.\n", rank);
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    // 5. Communication Logic: Even sends to Odd (0->1, 2->3, etc.)
    if (rank % 2 == 0) {
        // I am an EVEN rank (Sender)
        int partner = rank + 1;
        
        // Populate the array with some data to send
        for (int i = 0; i < N; i++) {
            data[i] = rank * 10 + i; // Just some dummy data based on rank
        }

        printf("Rank %d: Sending %d elements to Rank %d\n", rank, N, partner);
        
        // MPI_Send(buffer, count, datatype, destination, tag, communicator)
        MPI_Send(data, N, MPI_INT, partner, 0, MPI_COMM_WORLD);
        
    } else {
        // I am an ODD rank (Receiver)
        int partner = rank - 1;
        
        // MPI_Recv(buffer, count, datatype, source, tag, communicator, status)
        MPI_Recv(data, N, MPI_INT, partner, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        
        printf("Rank %d: Received %d elements from Rank %d (First element: %d)\n", 
               rank, N, partner, data[0]);
    }

    // 6. Clean up memory and finalize MPI
    free(data);
    MPI_Finalize();
    return 0;
}

