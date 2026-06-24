#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int main(int argc, char *argv[]) {

    int rank, size, N;
    int *data = NULL;

    FILE *tracefile;

    double start_time;
    double end_time;
    double elapsed_time;


    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);


    if (argc != 2) {

        if (rank == 0) {
            printf("Usage: mpirun -np <processes> %s <N>\n", argv[0]);
        }

        MPI_Finalize();
        return 1;
    }

    N = atoi(argv[1]);

    if (N <= 0) {

        if (rank == 0) {
            printf("Error: N must be positive.\n");
        }

        MPI_Finalize();
        return 1;
    }

    if (size % 2 != 0) {

        if (rank == 0) {
            printf("Error: Requires EVEN number of processes.\n");
        }

        MPI_Finalize();
        return 1;
    }


    data = (int *)malloc(N * sizeof(int));

    if (data == NULL) {

        printf("Rank %d failed memory allocation.\n", rank);

        MPI_Abort(MPI_COMM_WORLD, 1);
    }


    if (rank % 2 == 0) {

        // EVEN ranks SEND
        int partner = rank + 1;

        for (int i = 0; i < N; i++) {
            data[i] = rank * 10 + i;
        }

        printf("Rank %d: Sending %d elements to Rank %d\n",
               rank, N, partner);

        // START TIMER
        start_time = MPI_Wtime();

        MPI_Send(data,
                 N,
                 MPI_INT,
                 partner,
                 0,
                 MPI_COMM_WORLD);

        // END TIMER
        end_time = MPI_Wtime();

        elapsed_time = end_time - start_time;


        tracefile = fopen("adjacent_trace.csv", "a");

        if (tracefile != NULL) {

            fprintf(tracefile,
                    "%d,%d,%lu,%f\n",
                    rank,
                    partner,
                    (unsigned long)(N * sizeof(int)),
                    elapsed_time);

            fclose(tracefile);
        }

    } else {

        // ODD ranks RECEIVE
        int partner = rank - 1;

        MPI_Recv(data,
                 N,
                 MPI_INT,
                 partner,
                 0,
                 MPI_COMM_WORLD,
                 MPI_STATUS_IGNORE);

        printf("Rank %d: Received %d elements from Rank %d (First element: %d)\n",
               rank, N, partner, data[0]);
    }


    free(data);

    MPI_Finalize();

    return 0;
}

