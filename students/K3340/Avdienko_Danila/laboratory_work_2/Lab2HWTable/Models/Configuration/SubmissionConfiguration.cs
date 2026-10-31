using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Lab2HWTable.Models.Configuration;

public class SubmissionConfiguration : IEntityTypeConfiguration<Submission>
{
    public void Configure(EntityTypeBuilder<Submission> builder)
    {
        builder.HasKey(s => s.Id);
        builder.HasOne(s => s.Homework)
            .WithMany()
            .HasForeignKey(s => s.HomeworkId);
        builder.HasOne<IdentityUser>()
            .WithMany()
            .HasForeignKey(s => s.StudentId);
    }
}