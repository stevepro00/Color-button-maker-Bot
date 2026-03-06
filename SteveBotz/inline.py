from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from .database import sb
from .admin import parse_button_markup

@Client.on_inline_query()
async def inline_post_handler(client, inline_query: InlineQuery):
    query_text = inline_query.query.strip()
    user_posts = await sb.get_user_posts(inline_query.from_user.id)
    
    results = []
    
    for post in user_posts:
        if query_text and query_text.lower() not in post["post_id"].lower():
            continue
            
        reply_markup, text_content = parse_button_markup(post["raw_text"])
        
        preview_title = text_content[:40] + "..." if len(text_content) > 40 else text_content
        
        results.append(
            InlineQueryResultArticle(
                title=f"Post ID: {post['post_id']}",
                description=preview_title,
                input_message_content=InputTextMessageContent(
                    text_content,
                    disable_web_page_preview=True
                ),
                reply_markup=reply_markup
            )
        )
        
    if not results:
        results.append(
            InlineQueryResultArticle(
                title="No posts found",
                description="Save a post in the bot first!",
                input_message_content=InputTextMessageContent("I need to create a post first!")
            )
        )

    await inline_query.answer(results, cache_time=1, is_personal=True)
