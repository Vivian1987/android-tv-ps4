package org.androidtvps4.connectivity;
import android.app.Application;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.NetworkRequest;
import android.util.Log;
/** Keep a Wi-Fi-specific request alive so Ethernet's higher score does not
 * withdraw all Wi-Fi demand. This does not bind apps, change routes, toggle
 * radios, store credentials, or override Android's normal Ethernet preference.
 * Installed as a persistent system app; no foreground notification is needed.
 */
public final class ConnectivityKeeper extends Application {
 private ConnectivityManager.NetworkCallback callback;
 @Override public void onCreate() { super.onCreate(); ensureRequested(); }
 public synchronized void ensureRequested() {
  if(callback!=null)return;
  ConnectivityManager cm=getSystemService(ConnectivityManager.class);
  ConnectivityManager.NetworkCallback next=new ConnectivityManager.NetworkCallback(){
   @Override public void onAvailable(Network network){Log.i("AtvConnectivity","Wi-Fi available");}
   @Override public void onLost(Network network){Log.i("AtvConnectivity","Wi-Fi disconnected; request retained");}
  };
  NetworkRequest request=new NetworkRequest.Builder()
    .addTransportType(NetworkCapabilities.TRANSPORT_WIFI)
    .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET).build();
  try {cm.requestNetwork(request,next);callback=next;Log.i("AtvConnectivity","Wi-Fi request active");}
  catch(RuntimeException e){Log.e("AtvConnectivity","Unable to register Wi-Fi request",e);}
 }
}
