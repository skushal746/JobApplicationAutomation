package com.jobapp.service;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender mailSender;

    @Value("${spring.mail.from:noreply@jobapp.local}")
    private String fromAddress;

    public void sendWelcomeEmail(String toEmail) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setFrom(fromAddress);
        message.setTo(toEmail);
        message.setSubject("Welcome to Job Application Automation");
        message.setText(
            "Hi,\n\n" +
            "Your account has been created successfully.\n\n" +
            "You can now log in and start automating your job applications.\n\n" +
            "— The JobApp Team"
        );
        mailSender.send(message);
    }
}
