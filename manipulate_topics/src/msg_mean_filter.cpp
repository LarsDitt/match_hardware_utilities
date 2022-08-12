//Directly included within the hpp
template <class T>
MessageMeanFilter<T>::MessageMeanFilter(ros::NodeHandle &nh):MessageFilterBase<T>(nh)
{
    ros::NodeHandle priv("~");
    if(!priv.getParam("sample_number",this->samples_num_))
    {
        ROS_ERROR_STREAM("Parameter sample_number is not specified for MeanFilter!");
        throw std::runtime_error("Parameter sample_number is not specified for MeanFilter!");
        return;
    }
    else
    {
        this->buffer_=std::make_unique<boost::circular_buffer<T>>(this->samples_num_);
    } 
    this->server_.setCallback(boost::bind(&MessageMeanFilter::dynConfigcallback,this,_1,_2));     
}
template <class T>
T MessageMeanFilter<T>::filter()
{
    using namespace msg_operators;
    T ret;    
    // ret=std::accumulate(this->buffer_->begin(),this->buffer_->end(),T(),static_cast<T (*)(T,T)>(&operator+)); 
    ret=std::accumulate(this->buffer_->begin(),this->buffer_->end(),T(),static_cast<T (*)(T,T)>(&operator+))/this->samples_num_; 
   
    ret.header.stamp=ros::Time::now();
    return ret;
}
template <class T>
void MessageMeanFilter<T>::dynConfigcallback(manipulate_topics::MeanConfig &config,uint32_t level)
{
    
    if(config.samples<1)
    {
        this->samples_num_=1;   
    }
    else
    {
        this->samples_num_=config.samples; 
    }
    
    this->buffer_->set_capacity(this->samples_num_);
}
