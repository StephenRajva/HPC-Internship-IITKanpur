#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int main(int argc, char *argv[]) {
    int rank, size, N;
    int *data = NULL;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc != 2) {
        if (rank == 0) printf("Usage: mpirun -np <processes> %s <N>\n", argv[0]);
        MPI_Finalize();
        return 1;
    }

    N = atoi(argv[1]);
    if (size % 2 != 0) {
        if (rank == 0) printf("Error: Requires an EVEN number of processes.\n");
        MPI_Finalize();
        return 1;
    }

    data = (int *)malloc(N * sizeof(int));

    // --- PATTERN III LOGIC ---
    int half = size / 2;
    int partner = (size - 1) - rank; // Mirrored partner calculation

    if (rank < half) {
        // Left Side (Senders)
        for (int i = 0; i < N; i++) data[i] = rank * 10 + i;

        printf("Rank %d (Outer-Left): Sending to mirrored Rank %d\n", rank, partner);
        MPI_Send(data, N, MPI_INT, partner, 0, MPI_COMM_WORLD);
        
    } else {
        // Right Side (Receivers)
        MPI_Recv(data, N, MPI_INT, partner, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("Rank %d (Outer-Right): Received from mirrored Rank %d (First element: %d)\n", 
               rank, partner, data[0]);
    }
    // -------------------------

    free(data);
    MPI_Finalize();
    return 0;
}

