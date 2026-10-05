use std::error::Error;
use std::fmt;
use std::ops::Range;

/// یک سند متنی بازشده در ادیتور.
///
/// بازه‌ها بر اساس بایت UTF-8 هستند؛ بنابراین برای متن فارسی هم
/// باید ابتدا و انتهای بازه روی مرز یک نویسه باشند.
[derive(Debug, Clone)]
pub struct Document {
    text: String,
    revision: u64,
    saved_revision: u64,
}

[derive(Debug, Clone, PartialEq, Eq)]
pub enum EditError {
    InvalidRange,
    NotCharBoundary,
}

impl fmt::Display for EditError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidRange => {
                write!(f, "بازه‌ی ویرایش خارج از محدوده‌ی سند است")
            }
            Self::NotCharBoundary => {
                write!(f, "بازه‌ی ویرایش از میان یک نویسه‌ی UTF-8 عبور می‌کند")
            }
        }
    }
}

impl Error for EditError {}

impl Document {
    /// سندی با متن اولیه می‌سازد.
    /// متن اولیه به‌عنوان نسخه‌ی ذخیره‌شده در نظر گرفته می‌شود.
    pub fn new(text: impl Into<String>) -> Self {
        Self {
            text: text.into(),
            revision: 0,
            saved_revision: 0,
        }
    }

    pub fn text(&self) -> &str {
        &self.text
    }

    pub fn revision(&self) -> u64 {
        self.revision
    }

    pub fn is_dirty(&self) -> bool {
        self.revision != self.saved_revision
    }

    /// تعداد خط‌ها؛ سند خالی یک خط دارد و خط جدید انتهایی
    /// نیز یک خط خالی تازه ایجاد می‌کند.
    pub fn line_count(&self) -> usize {
        self.text.bytes().filter(|byte| *byte == b'\n').count() + 1
    }

    /// بخشی از متن را جایگزین می‌کند.
    ///
    /// range بازه‌ی بایتی UTF-8 است، نه شماره‌ی نویسه یا ستون صفحه.
    pub fn replace(
        &mut self,
        range: Range<usize>,
        replacement: &str,
    ) -> Result<(), EditError> {
        if range.start > range.end || range.end > self.text.len() {
            return Err(EditError::InvalidRange);
        }

        if !self.text.is_char_boundary(range.start)
            || !self.text.is_char_boundary(range.end)
        {
            return Err(EditError::NotCharBoundary);
        }

        if &self.text[range.clone()] == replacement {
            return Ok(());
        }

        self.text.replace_range(range, replacement);
        self.revision = self.revision.wrapping_add(1);

        Ok(())
    }

    /// پس از ذخیره‌ی موفق فایل، این متد را صدا بزن.
    pub fn mark_saved(&mut self) {
        self.saved_revision = self.revision;
    }
}

[cfg(test)]
mod tests {
    use super::{Document, EditError};

    #[test]
    fn replacing_text_marks_document_dirty() {
        let mut document = Document::new("hello");

        document.replace(0..5, "world").unwrap();

        assert_eq!(document.text(), "world");
        assert!(document.is_dirty());
    }
    #[test]
    fn marking_saved_clears_dirty_state() {
        let mut document = Document::new("سلام");

        document.replace(0..8, "درود").unwrap();
        document.mark_saved();

        assert!(!document.is_dirty());
    }

    #[test]
    fn rejects_range_inside_utf8_character() {
        let mut document = Document::new("سلام");

        let result = document.replace(1..2, "x");

        assert_eq!(result, Err(EditError::NotCharBoundary));
        assert_eq!(document.text(), "سلام");
    }

    #[test]
    fn counts_lines_including_trailing_empty_line() {
        let document = Document::new("اول\nدوم\n");

        assert_eq!(document.line_count(), 3);
    }
}
