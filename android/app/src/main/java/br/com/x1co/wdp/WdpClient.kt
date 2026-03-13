package br.com.x1co.wdp

import java.io.InputStream
import java.net.Socket
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager
import java.security.cert.X509Certificate

class WdpClient {
    fun fetch(url: String, callback: (Result<String>) -> Unit) {
        Thread {
            try {
                val isSecure = url.startsWith("wdps://")
                val cleanUrl = if (url.contains("://")) url.substringAfter("://") else url
                val parts = cleanUrl.split("/", limit = 2)
                val hostPort = parts[0]
                
                var host = hostPort
                var port = if (isSecure) 7071 else 7070
                
                if (hostPort.contains(":")) {
                    val hp = hostPort.split(":")
                    host = hp[0]
                    port = hp[1].toInt()
                }

                // Simplified Registry for Android
                if (host == "home") host = "46.225.97.140"

                val socket = if (isSecure) {
                    val sc = SSLContext.getInstance("TLS")
                    sc.init(null, arrayOf<TrustManager>(object : X509TrustManager {
                        override fun checkClientTrusted(p0: Array<out X509Certificate>?, p1: String?) {}
                        override fun checkServerTrusted(p0: Array<out X509Certificate>?, p1: String?) {}
                        override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
                    }), java.security.SecureRandom())
                    sc.socketFactory.createSocket(host, port)
                } else {
                    Socket(host, port)
                }

                socket.soTimeout = 7000
                socket.outputStream.write("WDP $url\r\n".toByteArray())
                
                val response = socket.inputStream.bufferedReader().use { it.readText() }
                
                val body = if (response.contains("\r\n\r\n")) {
                    response.substringAfter("\r\n\r\n")
                } else {
                    response
                }
                
                callback(Result.success(body))
                socket.close()
            } catch (e: Exception) {
                callback(Result.failure(e))
            }
        }.start()
    }
}
