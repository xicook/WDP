package br.com.x1co.wdp

import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.view.Gravity
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import com.bumptech.glide.Glide

class EasyWdlRenderer(private val context: Context, private val container: LinearLayout) {

    fun render(content: String) {
        container.removeAllViews()
        
        // Simple tokenization for EasyWDL
        val tagRegex = "\\(.*?\\)".toRegex()
        val tags = tagRegex.findAll(content).toList()
        val plainTexts = content.split(tagRegex)
        
        val combined = mutableListOf<String>()
        for (i in plainTexts.indices) {
            if (plainTexts[i].isNotEmpty()) combined.add(plainTexts[i])
            if (i < tags.size) combined.add(tags[i].value)
        }

        var currentTag: String? = null
        
        for (token in combined) {
            if (token.startsWith("(") && token.endsWith(")")) {
                val tagName = token.substring(1, token.length - 1).lowercase().split(":")[0]
                
                if (tagName == currentTag) {
                    currentTag = null
                    continue
                }
                currentTag = tagName
            } else {
                val text = token.trim()
                if (text.isEmpty()) continue

                when (currentTag) {
                    "title" -> addTextView(text, 26f, true, true)
                    "text" -> addTextView(text, 16f, false, false)
                    "center" -> addTextView(text, 16f, false, true)
                    "image" -> addImageView(text)
                    "link" -> addTextView(text, 16f, true, false, Color.BLUE)
                    else -> addTextView(text, 16f, false, false)
                }
            }
        }
    }

    private fun addTextView(text: String, size: Float, bold: Boolean, center: Boolean, color: Int = Color.BLACK) {
        val tv = TextView(context).apply {
            this.text = text
            this.textSize = size
            this.setTextColor(color)
            if (bold) setTypeface(null, Typeface.BOLD)
            if (center) gravity = Gravity.CENTER_HORIZONTAL
            setPadding(0, 12, 0, 12)
        }
        container.addView(tv)
    }

    private fun addImageView(url: String) {
        if (!url.startsWith("http")) return
        val iv = ImageView(context).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 20, 0, 20) }
            adjustViewBounds = true
        }
        Glide.with(context).load(url).into(iv)
        container.addView(iv)
    }
}
