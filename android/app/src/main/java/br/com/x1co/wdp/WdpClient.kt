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
                val hostPort = cleanUrl.split("/", "?").first()
                
                var resolvedHost: String
                var resolvedPort: Int

                // Official WDP Network Hardcoded Resolution
                val resolution = when (hostPort) {
                    "home", "x1co.com.br" -> "46.225.97.140:7070"
                    "search.me", "register.me", "portal.me" -> "46.225.97.140:5555"
                    else -> hostPort
                }

                if (resolution.contains(":")) {
                    val hp = resolution.split(":")
                    resolvedHost = hp[0]
                    resolvedPort = hp[1].toInt()
                } else {
                    resolvedHost = resolution
                    resolvedPort = if (isSecure) 7071 else 7070
                }

                val socket = if (isSecure) {
                    val sc = SSLContext.getInstance("TLS")
                    sc.init(null, arrayOf<TrustManager>(object : X509TrustManager {
                        override fun checkClientTrusted(p0: Array<out X509Certificate>?, p1: String?) {}
                        override fun checkServerTrusted(p0: Array<out X509Certificate>?, p1: String?) {}
                        override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
                    }), java.security.SecureRandom())
                    sc.socketFactory.createSocket(resolvedHost, resolvedPort)
                } else {
                    Socket(resolvedHost, resolvedPort)
                }

                socket.soTimeout = 7000
                socket.outputStream.write("WDP $url\r\n".toByteArray())
                
                // Read response
                val responseText = socket.inputStream.bufferedReader().use { it.readText() }
                
                val body = if (responseText.contains("\r\n\r\n")) {
                    responseText.substringAfter("\r\n\r\n")
                } else {
                    val firstNl = responseText.indexOf("\n")
                    if (firstNl != -1) responseText.substring(firstNl + 1).trim() else responseText
                }
                
                callback(Result.success(body))
                socket.close()
            } catch (e: Exception) {
                callback(Result.failure(e))
            }
        }.start()
    }
}
