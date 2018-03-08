/*********************************************
 *  pipe.c
 *  Socket Code for Text-Based Adventure Game
 *  COMP3411 Artificial Intelligence
 *  UNSW Session 1, 2017
*/

// YOU SHOULD NOT NEED TO MODIFY THIS FILE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h> 
#include <netinet/tcp.h>
#include <netdb.h>


int tcpopen(char *host, int port)
{   
  int sd, rc;
  struct hostent *h;
  struct sockaddr_in servAddr;
  
  h = (struct hostent *)gethostbyname(host);
  if(h==NULL) {
    printf("unknown host '%s'\n",host);
    exit(1);
  }

  servAddr.sin_family = h->h_addrtype;
  memcpy((char *) &servAddr.sin_addr.s_addr,h->h_addr_list[0],h->h_length);
  servAddr.sin_port = htons(port);

  /* create socket */
  sd = socket(AF_INET, SOCK_STREAM, 0);
  if(sd<0) {
    perror("cannot open socket ");
    exit(1);
  }
  
  int tcp_no_delay = 1;
  if(setsockopt(sd, IPPROTO_TCP, TCP_NODELAY,
           (char *)&tcp_no_delay, sizeof(tcp_no_delay)) < 0) {
    perror ("tcpecho: TCP_NODELAY options");
    exit(1);
  }

  /* connect to server */
  rc = connect(sd, (struct sockaddr *) &servAddr, sizeof(servAddr));
  if(rc<0) {
    perror("cannot connect ");
    exit(1);
  }

  return sd;
}
