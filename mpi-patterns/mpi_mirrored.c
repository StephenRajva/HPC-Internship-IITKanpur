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

        if(rank == 0)
            printf("Usage: mpirun -np <processes> %s <N>\n", argv[0]);

        MPI_Finalize();
        return 1;
    }

    N = atoi(argv[1]);

    if(size % 2 != 0) {

        if(rank == 0)
            printf("Requires EVEN number of processes\n");

        MPI_Finalize();
        return 1;
    }

    data = (int*) malloc(N * sizeof(int));

    int half = size / 2;
    int partner = (size - 1) - rank;

    double start_time, end_time;

    if(rank < half) {

        for(int i=0;i<N;i++)
            data[i] = rank * 10 + i;

        start_time = MPI_Wtime();

        MPI_Send(data, N, MPI_INT,
                 partner, 0, MPI_COMM_WORLD);

        end_time = MPI_Wtime();

        FILE *fp = fopen(
        "/Users/stephenrajva/Downloads/SST_Stimulator/Communication _Pattern/Mirrored_experiment/mirrored_trace.csv",
        "a");

        fprintf(fp,
                "%d,%d,%lu,%lf\n",
                rank,
                partner,
                (unsigned long)(N*sizeof(int)),
                end_time-start_time);

        fclose(fp);

    } else {

        MPI_Recv(data, N, MPI_INT,
                 partner, 0,
                 MPI_COMM_WORLD,
                 MPI_STATUS_IGNORE);
    }

    free(data);

    MPI_Finalize();

    return 0;
}
