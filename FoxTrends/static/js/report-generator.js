/**
 * 报告生成模块
 */

/**
 * 生成单个需求报告
 */
async function generateDemandReport(demandId) {
    try {
        const response = await fetch(`/api/demands/${demandId}/report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('报告生成成功！');
            // 在新窗口打开报告
            window.open(data.report_url, '_blank');
        } else {
            alert(`报告生成失败: ${data.message}`);
        }
    } catch (error) {
        console.error('生成报告失败:', error);
        alert('报告生成失败，请查看控制台');
    }
}

/**
 * 生成时间范围报告
 */
async function generateTimeRangeReport(startDate, endDate, communityIds = null) {
    try {
        const response = await fetch('/api/reports/time-range', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start_date: startDate,
                end_date: endDate,
                community_ids: communityIds
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('报告生成成功！');
            // 在新窗口打开报告
            window.open(data.report_url, '_blank');
        } else {
            alert(`报告生成失败: ${data.message}`);
        }
    } catch (error) {
        console.error('生成报告失败:', error);
        alert('报告生成失败，请查看控制台');
    }
}

/**
 * 显示时间范围报告对话框
 */
function showTimeRangeReportDialog() {
    const html = `
        <div class="modal-dialog show" id="time-range-report-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">生成时间范围报告</h3>
                    <button class="modal-close" onclick="closeTimeRangeReportDialog()">×</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">开始日期</label>
                        <input type="date" id="report-start-date" class="form-input" 
                               value="${new Date(Date.now() - 30*24*60*60*1000).toISOString().split('T')[0]}">
                    </div>
                    <div class="form-group">
                        <label class="form-label">结束日期</label>
                        <input type="date" id="report-end-date" class="form-input" 
                               value="${new Date().toISOString().split('T')[0]}">
                    </div>
                    <div class="form-group">
                        <label class="form-label">社区筛选（可选）</label>
                        <select id="report-communities" class="form-select" multiple>
                            <!-- 动态加载社区列表 -->
                        </select>
                        <span class="form-hint">按住 Ctrl/Cmd 可多选，不选则包含所有社区</span>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeTimeRangeReportDialog()">取消</button>
                    <button class="btn btn-primary" onclick="submitTimeRangeReport()">生成报告</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', html);
    
    // 加载社区列表
    loadCommunitiesForReport();
}

/**
 * 关闭时间范围报告对话框
 */
function closeTimeRangeReportDialog() {
    const dialog = document.getElementById('time-range-report-dialog');
    if (dialog) {
        dialog.remove();
    }
}

/**
 * 提交时间范围报告
 */
async function submitTimeRangeReport() {
    const startDate = document.getElementById('report-start-date').value;
    const endDate = document.getElementById('report-end-date').value;
    const select = document.getElementById('report-communities');
    
    // 获取选中的社区ID
    const selectedOptions = Array.from(select.selectedOptions);
    const communityIds = selectedOptions.length > 0 
        ? selectedOptions.map(opt => parseInt(opt.value))
        : null;
    
    if (!startDate || !endDate) {
        alert('请选择开始和结束日期');
        return;
    }
    
    // 转换为ISO格式
    const startDateTime = new Date(startDate).toISOString();
    const endDateTime = new Date(endDate + 'T23:59:59').toISOString();
    
    closeTimeRangeReportDialog();
    
    await generateTimeRangeReport(startDateTime, endDateTime, communityIds);
}

/**
 * 加载社区列表到报告对话框
 */
async function loadCommunitiesForReport() {
    try {
        const response = await fetch('/api/communities');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('report-communities');
            select.innerHTML = data.communities.map(c => 
                `<option value="${c.id}">${c.name} (${c.source_type})</option>`
            ).join('');
        }
    } catch (error) {
        console.error('加载社区列表失败:', error);
    }
}
