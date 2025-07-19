<template>
  <div class="admin-container">
    <h1>求职规划助手管理端</h1>
    
    <el-tabs v-model="activeTab">
      <el-tab-pane label="数据统计" name="statistics">
        <div class="statistics-container">
          <el-row :gutter="20">
            <el-col :span="8" v-for="stat in statistics" :key="stat.label">
              <el-card class="stat-card">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </el-card>
            </el-col>
          </el-row>
          
          <div class="system-info">
            <h3>系统信息</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="数据库名称">{{ systemInfo.collection_name || '加载中...' }}</el-descriptions-item>
              <el-descriptions-item label="数据存储路径">./data/chromadb</el-descriptions-item>
              <el-descriptions-item label="API 版本">1.0.0</el-descriptions-item>
              <el-descriptions-item label="服务器时间">{{ currentTime }}</el-descriptions-item>
            </el-descriptions>
          </div>
          
          <div class="recent-jobs">
            <h3>最近添加的职位</h3>
            <el-skeleton :rows="5" animated v-if="loading" />
            <el-table v-else :data="recentJobs" stripe>
              <el-table-column prop="title" label="职位名称" />
              <el-table-column prop="company" label="公司名称" />
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button size="small" type="primary" @click="viewJobDetail(scope.row.id)">查看</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="职位数据" name="jobs">
        <div class="jobs-container">
          <div class="search-form">
            <el-form :inline="true">
              <el-form-item label="搜索">
                <el-input v-model="searchQuery" placeholder="输入职位、公司、技能等关键词"></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="searchJobs">搜索</el-button>
              </el-form-item>
              <el-form-item>
                <el-select v-model="pageSize" @change="handleSizeChange">
                  <el-option :value="10" label="10条/页" />
                  <el-option :value="20" label="20条/页" />
                  <el-option :value="50" label="50条/页" />
                </el-select>
              </el-form-item>
            </el-form>
          </div>
          
          <el-table :data="jobs" stripe v-loading="loading">
            <el-table-column prop="metadata.job_title" label="职位名称" />
            <el-table-column prop="metadata.company_name" label="公司名称" />
            <el-table-column prop="metadata.location" label="工作地点" />
            <el-table-column prop="metadata.salary_range" label="薪资范围" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-button size="small" type="primary" @click="viewJobDetail(scope.row.id)">详情</el-button>
                <el-button size="small" type="danger" @click="confirmDelete(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination">
            <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page="currentPage"
              :page-sizes="[10, 20, 50]"
              :page-size="pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalItems"
            >
            </el-pagination>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 职位详情对话框 -->
    <el-dialog
      v-model="jobDetailVisible"
      title="职位详情"
      width="70%"
      destroy-on-close
    >
      <el-skeleton :rows="10" animated v-if="detailLoading" />
      <div v-else class="job-detail">
        <el-descriptions title="" :column="2" border>
          <el-descriptions-item label="职位名称">{{ currentJob.metadata?.job_title || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="公司名称">{{ currentJob.metadata?.company_name || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="工作地点">{{ currentJob.metadata?.location || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="薪资范围">{{ currentJob.metadata?.salary_range || '未知' }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="job-description">
          <h4>职位描述</h4>
          <p>{{ currentJob.metadata?.description || '无描述' }}</p>
        </div>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <h4>技能要求</h4>
            <el-tag
              v-for="(skill, index) in processSkills(currentJob.metadata?.skills)"
              :key="index"
              class="skill-tag"
            >
              {{ skill }}
            </el-tag>
          </el-col>
          <el-col :span="12">
            <h4>职位要求</h4>
            <ul>
              <li v-for="(req, index) in processRequirements(currentJob.metadata?.requirements)" :key="index">
                {{ req }}
              </li>
            </ul>
          </el-col>
        </el-row>
        
        <h4>向量嵌入文本</h4>
        <el-card>
          <div>{{ currentJob.document }}</div>
        </el-card>
        
        <h4>元数据</h4>
        <pre class="metadata-json">{{ JSON.stringify(currentJob.metadata, null, 2) }}</pre>
      </div>
      
      <template #footer>
        <el-button @click="jobDetailVisible = false">关闭</el-button>
        <el-button type="danger" @click="confirmDelete(currentJob.id)">删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiService } from '../api'

export default {
  name: 'AdminPanel',
  setup() {
    // 公共状态
    const loading = ref(false)
    const detailLoading = ref(false)
    const activeTab = ref('statistics')
    const currentTime = ref(new Date().toLocaleString())
    
    // 统计信息
    const statistics = ref([
      { label: '职位嵌入向量', value: 0 },
      { label: '用户嵌入向量', value: 0 },
      { label: '总嵌入向量', value: 0 }
    ])
    const systemInfo = ref({})
    const recentJobs = ref([])
    
    // 职位数据
    const jobs = ref([])
    const totalItems = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const searchQuery = ref('')
    
    // 职位详情
    const jobDetailVisible = ref(false)
    const currentJob = ref({})
    
    // 定时更新服务器时间
    setInterval(() => {
      currentTime.value = new Date().toLocaleString()
    }, 1000)
    
    // 初始化
    onMounted(() => {
      loadStatisticsData()
    })
    
    // 加载统计数据
    const loadStatisticsData = async () => {
      try {
        loading.value = true
        const response = await apiService.getChromaStats()
        
        statistics.value[0].value = response.job_embeddings
        statistics.value[1].value = response.user_embeddings
        statistics.value[2].value = response.total_embeddings
        
        systemInfo.value = response
        recentJobs.value = response.recent_jobs || []
      } catch (error) {
        console.error('Failed to load statistics:', error)
        ElMessage.error('加载统计数据失败')
      } finally {
        loading.value = false
      }
    }
    
    // 加载职位数据
    const loadJobsData = async () => {
      try {
        loading.value = true
        const params = {
          limit: pageSize.value,
          offset: (currentPage.value - 1) * pageSize.value
        }
        
        if (searchQuery.value) {
          params.query = searchQuery.value
        }
        
        const response = await apiService.getChromaJobs(params)
        jobs.value = response.results
        totalItems.value = response.total
      } catch (error) {
        console.error('Failed to load jobs:', error)
        ElMessage.error('加载职位数据失败')
      } finally {
        loading.value = false
      }
    }
    
    // 查看职位详情
    const viewJobDetail = async (jobId) => {
      try {
        detailLoading.value = true
        jobDetailVisible.value = true
        
        const job = await apiService.getChromaJobDetail(jobId)
        currentJob.value = job
      } catch (error) {
        console.error('Failed to load job detail:', error)
        ElMessage.error('加载职位详情失败')
      } finally {
        detailLoading.value = false
      }
    }
    
    // 处理技能列表
    const processSkills = (skills) => {
      if (!skills) return []
      if (Array.isArray(skills)) return skills
      if (typeof skills === 'string') return skills.split(',').map(s => s.trim())
      return []
    }
    
    // 处理需求列表
    const processRequirements = (requirements) => {
      if (!requirements) return []
      if (Array.isArray(requirements)) return requirements
      if (typeof requirements === 'string') return requirements.split(',').map(r => r.trim())
      return []
    }
    
    // 确认删除
    const confirmDelete = (jobId) => {
      ElMessageBox.confirm(
        '确定要删除这个职位数据吗？此操作不可恢复。',
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        deleteJob(jobId)
      }).catch(() => {
        // 取消删除
      })
    }
    
    // 删除职位
    const deleteJob = async (jobId) => {
      try {
        loading.value = true
        await apiService.deleteChromaJob(jobId)
        ElMessage.success('职位已成功删除')
        
        // 关闭详情对话框
        jobDetailVisible.value = false
        
        // 重新加载数据
        if (activeTab.value === 'statistics') {
          loadStatisticsData()
        } else {
          loadJobsData()
        }
      } catch (error) {
        console.error('Failed to delete job:', error)
        ElMessage.error('删除职位失败')
      } finally {
        loading.value = false
      }
    }
    
    // 搜索职位
    const searchJobs = () => {
      currentPage.value = 1
      loadJobsData()
    }
    
    // 切换页面大小
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      loadJobsData()
    }
    
    // 切换页码
    const handleCurrentChange = (page) => {
      currentPage.value = page
      loadJobsData()
    }
    
    // 监听标签页切换
    const watchActiveTab = computed(() => {
      if (activeTab.value === 'jobs' && jobs.value.length === 0) {
        loadJobsData()
      }
      return activeTab.value
    })
    
    return {
      // 公共状态
      loading,
      detailLoading,
      activeTab,
      currentTime,
      watchActiveTab,
      
      // 统计信息
      statistics,
      systemInfo,
      recentJobs,
      
      // 职位数据
      jobs,
      totalItems,
      currentPage,
      pageSize,
      searchQuery,
      
      // 职位详情
      jobDetailVisible,
      currentJob,
      
      // 方法
      loadStatisticsData,
      loadJobsData,
      viewJobDetail,
      confirmDelete,
      searchJobs,
      handleSizeChange,
      handleCurrentChange,
      processSkills,
      processRequirements
    }
  }
}
</script>

<style scoped>
.admin-container {
  padding: 20px;
}

.statistics-container, .jobs-container {
  margin-top: 20px;
}

.stat-card {
  text-align: center;
  margin-bottom: 20px;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 0.9rem;
  color: #909399;
}

.system-info, .recent-jobs {
  margin-top: 30px;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

.skill-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.job-description {
  margin-top: 20px;
  margin-bottom: 20px;
}

.metadata-json {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 200px;
  font-family: monospace;
}
</style>
