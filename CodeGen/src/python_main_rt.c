#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <sched.h>
#include <signal.h>
#include <unistd.h>
#include <sys/mman.h>
#include <string.h>
#include <fcntl.h>
#include <pthread.h>
#include <sys/io.h>

#ifdef CANOPEN
  void canopen_synch(void);
#endif

#define XNAME(x,y)  x##y
#define NAME(x,y)   XNAME(x,y)

int NAME(MODEL,_init)(void);
int NAME(MODEL,_isr)(double);
int NAME(MODEL,_end)(void);
double NAME(MODEL,_get_tsamp)(void);

#define NSEC_PER_SEC    1000000000
#define USEC_PER_SEC	1000000

static volatile int end = 0;
static double T = 0.0;

/* Options presettings */
static char rtversion[] = "0.9";
static int prio = 99;
static int verbose = 0;
static int wait = 0;
double FinalTime = 0.0;

double get_run_time()
{
  return(T);
}

static inline void tsnorm(struct timespec *ts)
{
  while (ts->tv_nsec >= NSEC_PER_SEC) {
    ts->tv_nsec -= NSEC_PER_SEC;
    ts->tv_sec++;
  }
}

static inline double calcdiff(struct timespec t1, struct timespec t2)
{
  long diff;
  diff = USEC_PER_SEC * ((long) t1.tv_sec - (long) t2.tv_sec);
  diff += ((int) t1.tv_nsec - (int) t2.tv_nsec) / 1000;
  return (1e-6*diff);
}


void *rt_task(void *p)
{
  struct timespec t, interval, curtime, T0;
  struct sched_param param;

  param.sched_priority = prio;
  if(sched_setscheduler(0, SCHED_FIFO, &param)==-1){
    perror("sched_setscheduler failed");
    exit(-1);
  }

  mlockall(MCL_CURRENT | MCL_FUTURE);

  double Tsamp = NAME(MODEL,_get_tsamp)();

  interval.tv_sec =  0L;
  interval.tv_nsec = (long)(1e9*Tsamp);
  tsnorm(&interval);

  T=0;

  NAME(MODEL,_init)();
  
#ifdef CANOPEN
  canopen_synch();
#endif
  
  /* get current time */
  clock_gettime(CLOCK_MONOTONIC,&t);

  /* start after one Tsamp */
  t.tv_sec+=interval.tv_sec;
  t.tv_nsec+=interval.tv_nsec;
  tsnorm(&t);

  T0 = t;

  while(!end){
   /* wait untill next shot */
    clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &t, NULL);

    /* Task time T */
    clock_gettime(CLOCK_MONOTONIC,&curtime);
    T = calcdiff(curtime,T0);

    /* periodic task */
#ifdef CANOPEN
  canopen_synch();
#endif
  
    NAME(MODEL,_isr)(T);

#ifdef CANOPEN
  canopen_synch();
#endif

  /* Check task end */
    if((FinalTime >0) && (T >= FinalTime)) pthread_exit(0);

    /* calculate next shot */
    t.tv_sec+=interval.tv_sec;
    t.tv_nsec+=interval.tv_nsec;
    tsnorm(&t);
  }
  NAME(MODEL,_end)();  
}

void endme(int n)
{
  end = 1;
}

void print_usage(void)
{
  puts(  "\nUsage:  'RT-model-name' [OPTIONS]\n"
         "\n"
         "OPTIONS:\n"
         "  -h  print usage\n"
	 "  -v  verbose output\n"
	 "  -p <priority>  set rt task priority (default 99)\n"
	 "  -e  external clock\n"
	 "  -w  wait to start\n"
	 "  -V  print version\n"
	 "\n");
}

static void proc_opt(int argc, char *argv[])
{
  int i;
  while((i=getopt(argc,argv,"ef:hp:vVw"))!=-1){
    switch(i){
    case 'h':
      print_usage();
      exit(0);
      break;
    case 'p':
      prio = atoi(optarg);
      break;
    case 'v':
      verbose = 1;
      break;
    case 'w':
      wait = 1;
      break;
    case 'V':
      printf("Version %s\n",rtversion);
      exit(0);
      break;
    case 'f':
      if (strstr(optarg, "inf")) {
        FinalTime = 0.0;
      } else if ((FinalTime = atof(optarg)) <= 0.0) {
        printf("-> Invalid final time.\n");
        exit(1);
      }
      break;
    }
  }
}

int main(int argc,char** argv)
{
  pthread_t thrd;
  pthread_attr_t t_att;
  int ap;
  int fd;
  int uid;

  proc_opt(argc, argv);

  signal(SIGINT,endme);
  signal(SIGKILL,endme);

  uid = geteuid();
  if (uid!=0){
    fd=open("/dev/nrt",O_RDWR);
    if (fd<0){
      printf("This SW needs superuser privilegies to run!\n");
      exit(1);
    }
    close(fd);
  }

  iopl(3);

  ap=pthread_create(&thrd,NULL,rt_task,NULL);

  pthread_join(thrd,NULL);
  close(fd);
}

