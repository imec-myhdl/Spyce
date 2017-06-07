void sendMsg(WORD ID, BYTE DATA[], int len);
int rcvMsg(BYTE DATA[], int timeout);
int rcvMsgCob(int cob, BYTE DATA[], int timeout);
int canOpen();
void canClose();
void canopen_synch();
