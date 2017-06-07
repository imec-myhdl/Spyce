/*
COPYRIGHT (C) 2016  Roberto Bucher (roberto.bucher@supsi.ch)

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
*/

#include <pyblock.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dlfcn.h>
#include <fmi2_cs.h>

#include <fmi2TypesPlatform.h>
#include <fmi2Functions.h>
#include <fmi2FunctionTypes.h>

double get_run_time();

extern const char *C_GUID;

static void callbackLogger(fmi2ComponentEnvironment c, fmi2String instanceName,
                           fmi2Status status, fmi2String category,
                           fmi2String message,...)
{
  /* fprintf(stderr,"-> %s\n",message); */
}

fmi2CallbackFunctions cbf = {callbackLogger, calloc, free, NULL, NULL};

static void init(python_block *block)
{
  int * intPar = block->intPar;
  char *guid;
  char *cmd;
  
  int pos = 0;
  int len;

  len =strlen(block->str);
  
  do{
    pos++;
  }while((block->str[pos]!='|') && (pos<len));
  if(pos==len) exit(1);

  guid = (char *) malloc(pos+1);
  cmd = (char*) malloc(len-pos+25);

  strncpy(guid, block->str, pos);
  guid[pos]='\0';

  /* sprintf(cmd,"unzip -o %s.fmu > /dev/null",&(block->str[pos+1])); */
  /* system(cmd); */

  /* Initialize the FMU component */
  
  fmi2Status ret;

  fmi2Component myC = fmi2Instantiate(&(block->str[pos+1]),
				      fmi2CoSimulation,
				      guid,
				      "file:///tmp",
				      &cbf, fmi2True, fmi2True);
  if(myC == NULL) exit(1);

  ret = fmi2SetupExperiment(myC, fmi2False, 0.0, 0.0, fmi2False, 0.0);
  if(ret) exit(1);

  ret = fmi2EnterInitializationMode(myC);
  if(ret) exit(1);
  
  ret = fmi2ExitInitializationMode(myC);
  if(ret) exit(1);
  
  block->ptrPar = (void *) myC;
}

static void inout(python_block *block)
{
  fmi2Status ret;
  fmi2Component myC = (fmi2Component) block->ptrPar;
  fmi2Real inp[3];
  fmi2Real out[3];
  
  int i;
  int * intPar = block->intPar;
  double * realPar    = block->realPar;
  int len_in, len_out;
  double t, dt;
  double *u;
  double *y;
  
  t = get_run_time();
  dt = realPar[0];
  
  len_in = intPar[0];
  len_out = intPar[1]; 

  /* Update the outputs */
  ret = fmi2GetReal(myC, &intPar[2+len_in], len_out, out);
  if(ret) exit(1);

  for(i=0;i<len_out;i++){
    y = (double *) block->y[i];
    y[0] = (double) out[i];
  }
  
  /* Set the inputs */
  for(i=0;i<len_in;i++){
    u = (double *) block->u[i];
    inp[i] = (fmi2Real) u[0];
  }
  ret = fmi2SetReal(myC, &intPar[2], len_in, inp);
  if(ret) exit(1);

  /* Perform the integration step */
  do{
    ret = fmi2DoStep(myC,t,dt,fmi2True);
  }while(ret!=fmi2OK);
}

static void end(python_block *block)
{
  fmi2Status ret;
  fmi2Component myC = (fmi2Component) block->ptrPar;
  fmi2Terminate(myC);
  fmi2FreeInstance (myC);
  /* system("rm -r binaries sources resources"); */
}

void FMUinterface(int flag, python_block *block)
{
  if (flag==OUT){          /* get input */
    inout(block);
  }
  else if (flag==END){     /* termination */ 
    end(block);
  }
  else if (flag ==INIT){    /* initialisation */
    init(block);
  }
}


