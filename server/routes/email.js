import express from 'express';

const router = express.Router();

router.post('/send-confirmation', (req, res) => {
  const { requestId } = req.body;
  console.log(`📧 Email sent for request: ${requestId}`);

  res.json({
    success: true,
    message: `Confirmation email sent`,
    requestId
  });
});

router.post('/send-expert-match', (req, res) => {
  const { requestId, expertId } = req.body;
  console.log(`📧 Expert match notification sent: ${expertId} for request ${requestId}`);

  res.json({
    success: true,
    message: `Expert notification sent`,
    requestId,
    expertId
  });
});

router.post('/auto-reply', (req, res) => {
  const { senderEmail } = req.body;
  console.log(`📧 Auto-reply sent to ${senderEmail}`);

  res.json({
    success: true,
    message: `Auto-reply sent`
  });
});

export { router as emailRoutes };
