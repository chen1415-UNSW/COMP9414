/*******************************************
 *  Raft.java 
 *  Engine for Text-Based Adventure Game
 *  COMP3411 Artificial Intelligence
 *  UNSW Session 1, 2017
*/

import java.util.*;
import java.io.*;
import java.net.*;

public class Raft {

   final static int EAST   = 0;
   final static int NORTH  = 1;
   final static int WEST   = 2;
   final static int SOUTH  = 3;

   private char[][] map;
   private char[][] view;

   private int nrows;     // number of rows in environment
   private int irow,icol; // initial row and column

    // current row, column and direction of agent
   private int row,col,dirn;

   private boolean have_axe     = false;
   private boolean have_key     = false;
   private boolean have_treasure= false;
   private boolean have_raft    = false;
   private boolean on_raft      = false;
   private boolean off_map      = false;

   private boolean game_won     = false;
   private boolean game_lost    = false;

   private int num_dynamites_held = 0;

   private static void swanSong( String message ) {
      System.out.println( message );
      System.exit(-1);
   }

   private void read_map( String mapName ) {

      BufferedReader in;
      boolean agent_here;
      char ch;
      int r,c;

      map = new char[1024][];

      r=-1;
      try {
         in = new BufferedReader(new FileReader(mapName));
         String oneLine = in.readLine();
         while(( oneLine != null )&&( oneLine.length() > 0 )) {
            map[++r] = new char[oneLine.length()];
            for( c=0; c < oneLine.length(); c++ ) {
               map[r][c] = oneLine.charAt(c);
               agent_here = true;
               switch( map[r][c] ) {
                case '^': dirn = NORTH; break;
                case '>': dirn = EAST;  break;
                case 'v': dirn = SOUTH; break;
                case '<': dirn = WEST;  break;
                default:  agent_here = false;
               }
               if( agent_here ) {
                  row = r;
                  col = c;
               }
            }
            oneLine = in.readLine();
         }
      }
      catch( FileNotFoundException fnfe ) {
         swanSong( "File Not Found: "+ mapName );
      }
      catch( IOException ioe ) {
         swanSong( "IO Error" );
      }

      nrows = r+1; // number of rows
      irow  = row; // initial row
      icol  = col; // initial column
   }

   private void print_map() {
      char ch=' ';
      int r,c;

      System.out.println();
      for( r=0; r < nrows; r++ ) {
         for( c=0; c < map[r].length; c++ ) {
            if(( r == row )&&( c == col )) { // agent is here
               switch( dirn ) {
                case NORTH: ch = '^'; break;
                case EAST:  ch = '>'; break;
                case SOUTH: ch = 'v'; break;
                case WEST:  ch = '<'; break;
               }
            }
            else {
              ch = map[r][c];
            }
            System.out.print( ch );
         }
         System.out.println();
      }
      System.out.println();
   }

   private boolean apply( char action )
   {
      int d_row, d_col;
      int new_row, new_col;
      char ch;

      if(( action == 'L' )||( action == 'l' )) {
         dirn = ( dirn + 1 ) % 4;
         return( true );
      }
      else if(( action == 'R' )||( action == 'r' )) {
         dirn = ( dirn + 3 ) % 4;
         return( true );
      }
      else {
         d_row = 0; d_col = 0;
         switch( dirn ) {
          case NORTH: d_row = -1; break;
          case SOUTH: d_row =  1; break;
          case EAST:  d_col =  1; break;
          case WEST:  d_col = -1; break;
         }
         new_row = row + d_row;
         new_col = col + d_col;

         if(  (new_row < 0)||(new_row >= nrows)
            ||(new_col < 0)||(new_col >= map[new_row].length)) {
            if(( action == 'F' )||( action == 'f' )) {
               if( !off_map ) {
                  map[row][col] = '~';
                  off_map = true;
               }
               row = new_row;
               col = new_col;
               game_lost = true;
               return( true );
            }
            else {
               return( false );
            }
         }

         ch = map[new_row][new_col];

         switch( action ) {
         case 'F': case 'f':
            switch( ch ) { // can't move into an obstacle
            case '*': case 'T': case '-':
               return( false );
            }
            if( !off_map ) map[row][col] = ' ';

            switch( ch ) {
             case '~':
                if( on_raft ) {
                    if( !off_map ) map[row][col] = '~';
                }
		else if( have_raft ) {
		    on_raft = true;
		    if( !off_map ) map[row][col] = ' ';
		}
                else {
                    game_lost = true;
                }
                break;
             case ' ': case 'a': case 'k': case '$': case 'd':
		if( on_raft && !off_map ) {
		    map[row][col] = '~';
		    on_raft = false;
		    have_raft = false;
		}
                break;
            }
            row = new_row;
            col = new_col;

            switch( ch ) {
             case 'a': have_axe      = true; break;
             case 'k': have_key      = true; break;
             case '$': have_treasure = true; break;
             case 'd': num_dynamites_held++; break;
            }
            if( have_treasure &&( row == irow )&&( col == icol )) {
               game_won = true;
            }
            if( !off_map ) map[row][col] = ' ';
            off_map = false;
            return( true );

         case 'C': case 'c': // chop
            if(( ch == 'T' )&& have_axe ) {
               map[new_row][new_col] = ' ';
	       have_raft = true;
               return( true );
            }
            break;

         case 'U': case 'u': // unlock
            if(( ch == '-' )&& have_key ) {
               map[new_row][new_col] = ' ';
               return( true );
            }
            break;

         case 'B': case 'b': // blast
            if( num_dynamites_held > 0 ) {
               switch( ch ) {
               case '*': case 'T': case '-':
                  map[new_row][new_col] = ' ';
                  num_dynamites_held--;
                  return( true );
               }
            }
            break;
         }
      }
      return( false );
   }

   private void get_view() {
      char ch;
      int i,j,r=0,c=0;

      for( i = -2; i <= 2; i++ ) {
         for( j = -2; j <= 2; j++ ) {
            switch( dirn ) {
             case NORTH: r = row+i; c = col+j; break;
             case SOUTH: r = row-i; c = col-j; break;
             case EAST:  r = row+j; c = col-i; break;
             case WEST:  r = row-j; c = col+i; break;
            }
            if(  ( r >= 0 )&&( r < nrows )
               &&( c >= 0 )&&( c < map[r].length )) {
                view[2+i][2+j] = map[r][c];
            }
            else {
                view[2+i][2+j] = '.';
            }
         }
      }
   }

   private static void printUsage()
   {
      swanSong(
        "Usage: java Raft [-p <port>] -i map [-m <maxmoves>] [-s]\n");
   }

   public static void main( String[] args )
   {
      Raft raft;
      boolean silent = false;
      String mapName = "";
      char action  = 'F';
      int maxmoves = 10000;
      int port = 0;
      int k,m;

      raft = new Raft();
      raft.view = new char[5][5];

      k=0;
      while( k < args.length ) {
         if( args[k].compareTo("-i") == 0 ) {
            if( ++k < args.length ) {
               mapName = args[k++];
            }
            else {
               printUsage();
            }
         }
         else if( args[k].compareTo("-p") == 0 ) {
            if( ++k < args.length ) {
               port = Integer.parseInt(args[k++]);
            }
            else {
               printUsage();
            }
         }
         else if( args[k].compareTo("-m") == 0 ) {
            if( ++k < args.length ) {
               maxmoves = Integer.parseInt(args[k++]);
            }
            else {
               printUsage();
            }
         }
         else if( args[k].compareTo("-s") == 0 ) {
            silent = true;
            k++;
         }
         else {
            printUsage();
         }
      }

      if( mapName.length() == 0 ) {
         printUsage();
      }
      raft.read_map( mapName );

      if( !silent ) {
         raft.print_map();
      }

      if( port != 0 ) {
         InputStream in            = null;
         OutputStream out          = null;
         ServerSocket serverSocket = null;
         Socket clientSocket       = null;
         int i,j;

         try {
            serverSocket = new ServerSocket( port );
            clientSocket = serverSocket.accept();
            serverSocket.close();
            in  = clientSocket.getInputStream();
            out = clientSocket.getOutputStream();
         }
         catch( IOException e ) {
            swanSong( "Could not listen on port: "+ port );
         }

         try {
            for( m=1; m <= maxmoves; m++ ) {
               raft.get_view();
               for( i=0; i < 5; i++ ) {
                   for( j=0; j < 5; j++ ) {
                       if( !(( i == 2 )&&( j == 2 ))) {
                          out.write( raft.view[i][j] );
                       }
                   }
               }
               out.flush();
               action = (char) in.read();
               if( !silent ) {
                 System.out.println("action = "+ action );
               }
               raft.apply( action );
               if( !silent ) {
                  raft.print_map();
               }
               if( raft.game_won ) {
                  swanSong( "Game Won in "+ m +" moves." );
               }
               else if( raft.game_lost ) {
                  swanSong( "Game Lost." );
               }
            }
            swanSong("Exceeded maximum of "+ maxmoves +" moves.\n");
         }
         catch( IOException e ) {
            swanSong("Lost connection to port: "+ port );
         }
         finally {
            try {
                clientSocket.close();
            }
            catch( IOException e ) {}
         }
      }
      else {
         Agent agent = new Agent();

         for( m=1; m <= maxmoves; m++ ) {
            raft.get_view();
            action = agent.get_action( raft.view );
            raft.apply( action );
            if( !silent ) {
               raft.print_map();
            }
            if( raft.game_won ) {
               swanSong( "Game Won in "+ m +" moves." );
            }
            else if( raft.game_lost ) {
               swanSong( "Game Lost." );
            }
         }
         swanSong("Exceeded maximum of "+ maxmoves +" moves.");
      }
   }
}
